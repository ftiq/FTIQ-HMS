/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";

export class AcsHmsDashTable {

    constructor(orm, state, action) {
        this.orm = orm
        this.state = state;
        this.action = action
    }

    async getAppointmentTable(offset = 0, limit = 20) {
        try {
            var appointmentTableData = await this.orm.call(
                'acs.hms.dashboard', 
                'acs_get_appointment_table_data', 
                [this.state.date_domain, offset, limit]
            );
            if (appointmentTableData) {
                this.state.appointmentsTable = appointmentTableData;
            }
        } catch (error) {
            console.error(_t("Error fetching Appointments Table:"), error);
        }
    }

    openAppointment(appointmentId) {
        this.orm.call('hms.appointment', 'read', [[appointmentId], ['id']]).then((result) => {
            if (result && result.length) {
                return this.action.doAction({
                    type: 'ir.actions.act_window',
                    name: _t('Appointment'),
                    res_model: 'hms.appointment',
                    res_id: appointmentId,
                    views: [[false, 'form']],
                    target: 'current',
                });
            } else {
                console.error("No appointment found with this ID.");
            }
        }).catch((error) => {
            console.error("Error opening Appointment record:", error);
        });
    }
}