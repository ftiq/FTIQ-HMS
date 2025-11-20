/** @almightycs-module */

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";

patch(ControlButtons.prototype, {
    onClickPrescription() {
        this.dialog.add(SelectCreateDialog, {
            resModel: "prescription.order",
            noCreate: true,
            multiSelect: false,
            domain: [
                ["state", "=", "prescription"],
                ["acs_pos_processed", "=", false],
                ["currency_id", "=", this.pos.currency.id],
            ],
            onSelected: async (resIds) => {
                await this.pos.onClickPrescriptionOrder(resIds[0]);
            },
        });
    },
});
