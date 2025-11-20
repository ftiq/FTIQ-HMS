import { CalendarCommonPopover } from "@web/views/calendar/calendar_common/calendar_common_popover";
import { onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class AcsCalendarCommonPopover extends CalendarCommonPopover {
    
    static subTemplates = {
        ...CalendarCommonPopover.subTemplates,
        footer: "acs_hms_nursing.AcsCalendarCommonPopover.footer",
    };

    setup() {
        super.setup();
        this.actionService = useService("action");
        this.orm = useService("orm");
        this.viewType = "calendar";
        onWillStart(async () => {
            this.record = this.props.record.rawRecord;
            this.state = this.record.state;
        });
    }

    async onClickButton(ev) {
        const action = await this.orm.call("acs.patient.medication", ev.target.name, [this.record.id]);
        if (action && action.type === "ir.actions.act_window") {
            this.actionService.doAction(action);
        } else {
            await this.props.model.load();
            this.props.close();
        }
    }
}