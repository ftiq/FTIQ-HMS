import { _t } from "@web/core/l10n/translation";
import { parseFloat } from "@web/views/fields/parsers";
import { SelectionPopup } from "@point_of_sale/app/components/popups/selection_popup/selection_popup";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { NumberPopup } from "@point_of_sale/app/components/popups/number_popup/number_popup";
import { ask, makeAwaitable } from "@point_of_sale/app/utils/make_awaitable_dialog";
import { enhancedButtons } from "@point_of_sale/app/components/numpad/numpad";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { accountTaxHelpers } from "@account/helpers/account_tax";
import { getTaxesAfterFiscalPosition } from "@point_of_sale/app/models/utils/tax_utils";


patch(PosStore.prototype, {
    async onClickPrescriptionOrder(clickedOrderId) {
        const selectedOption = await makeAwaitable(this.dialog, SelectionPopup, {
            title: _t("What do you want to do?"),
            list: [
                { id: "0", label: _t("Settle the order"), item: "settle" },
            ],
        });
        if (!selectedOption) {
            return;
        }
        const prescription_order = await this._getPrescriptionOrder(clickedOrderId);

        const currentPrescriptionOrigin = this.getOrder()
            .getOrderlines()
            .find((line) => line.prescription_order_origin_id)?.prescription_order_origin_id;
        if (currentPrescriptionOrigin?.id) {
            const linkedSO = await this._getPrescriptionOrder(currentPrescriptionOrigin.id);
            if (
                linkedSO.partner_id?.id !== prescription_order.partner_id?.id ||
                linkedSO.partner_invoice_id?.id !== prescription_order.partner_invoice_id?.id ||
                linkedSO.partner_shipping_id?.id !== prescription_order.partner_shipping_id?.id
            ) {
                this.add_new_order({
                    partner_id: prescription_order.partner_id,
                });
                this.notification.add(_t("A new order has been created."));
            }
        }
        const orderFiscalPos =
            prescription_order.fiscal_position_id &&
            this.models["account.fiscal.position"].find(
                (position) => position.id === prescription_order.fiscal_position_id
            );
        if (orderFiscalPos) {
            this.getOrder().update({
                fiscal_position_id: orderFiscalPos,
            });
        }
        if (prescription_order.partner_id) {
            this.getOrder().setPartner(prescription_order.partner_id);
        }
        await this.settleSO(prescription_order, orderFiscalPos);
        this.selectOrderLine(this.getOrder(), this.getOrder().lines.at(-1));
    },
    async _getPrescriptionOrder(id) { 
        const result = await this.data.callRelated("prescription.order", "load_prescription_order_from_pos", [
            id,
            this.config.id,
        ]);
        return result["prescription.order"][0];
    },
    async settleSO(prescription_order, orderFiscalPos) {
        if (prescription_order.pricelist_id) {
            this.getOrder().setPricelist(prescription_order.pricelist_id);
        }
        let useLoadedLots = false;
        let userWasAskedAboutLoadedLots = false;
        let previousProductLine = null;
        for (const line of prescription_order.prescription_line_ids) {
            if (line.display_type === "line_note") {
                if (previousProductLine) {
                    const previousNote = previousProductLine.customer_note;
                    previousProductLine.customer_note = previousNote
                        ? previousNote + "--" + line.name
                        : line.name;
                }
                continue;
            }
            const taxes = getTaxesAfterFiscalPosition(line.tax_ids, orderFiscalPos, this.models);
            const newLineValues = {
                product_tmpl_id: line.product_id?.product_tmpl_id,
                product_id: line.product_id,
                qty: line.product_uom_qty,
                price_unit: line.price_unit,
                price_type: "automatic",
                tax_ids: taxes.map((tax) => ["link", tax]),
                prescription_order_origin_id: prescription_order,
                prescription_order_line_id: line,
                customer_note: line.customer_note,
                description: line.name,
                order_id: this.getOrder()
            };
            if (line.display_type === "line_section") {
                continue;
            }
            const newLine = await this.addLineToCurrentOrder(newLineValues, {}, false);
            previousProductLine = newLine;
            if (
                newLine.getProduct().tracking !== "none" &&
                (this.pickingType.use_create_lots || this.pickingType.use_existing_lots) &&
                line.pack_lot_ids?.length > 0
            ) {
                if (!useLoadedLots && !userWasAskedAboutLoadedLots) {
                    useLoadedLots = await ask(this.dialog, {
                        title: _t("SN/Lots Loading"),
                        body: _t("Do you want to load the SN/Lots linked to the Prescriptions Order?"),
                    });
                    userWasAskedAboutLoadedLots = true;
                }
                if (useLoadedLots) {
                    newLine.setPackLotLines({
                        modifiedPackLotLines: [],
                        newPackLotLines: (line.lot_names || []).map((name) => ({
                            lot_name: name,
                        })),
                    });
                }
            }
            newLine.setQuantityFromPOL(line);
            newLine.setUnitPrice(line.price_unit);
            newLine.setDiscount(line.discount);

            const product_unit = line.product_id.uom_id;
            if (product_unit && !product_unit.is_pos_groupable) {
                let remaining_quantity = newLine.qty;
                newLine.delete();
                while (!this.env.utils.floatIsZero(remaining_quantity)) {
                    const splitted_line = this.models["pos.order.line"].create({
                        ...newLineValues,
                    });
                    splitted_line.setQuantity(Math.min(remaining_quantity, 1.0), true);
                    remaining_quantity -= splitted_line.qty;
                }
            }
        }
    },
});
