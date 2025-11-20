/** @odoo-module **/

import { user } from "@web/core/user";
import { _t } from "@web/core/l10n/translation";

export class AcsHmsDashAction {
    constructor(state, action) {
        this.state = state;
        this.action = action || {};

        if (!this.action.acsOpenAction) {
            this.action.acsOpenAction = () => {
                console.error("acsOpenAction is undefined. Make sure the 'action' object has this method.");
            };
        }
    }
    
    async acsOpenPatients() {
        return this.action.acsOpenAction(
            "Patients",
            "hms.patient",
            this.state.domain,
            [[false, "kanban"], [false, "list"], [false, "form"]],
        );
    }

    async acsOpenMyPatients() {
        return this.action.acsOpenAction(
            "My Patients",
            "hms.patient",
            [['primary_physician_id.user_id','=',user.userId], ...this.state.domain],
            [[false, "kanban"], [false, "list"], [false, "form"]],
        );
    }

    async acsOpenPhysicians() {
        return this.action.acsOpenAction(
            "Physicians",
            "hms.physician",
            this.state.domain,
            [[false, "kanban"], [false, "list"], [false, "form"]],
        );
    }

    async acsOpenReferringPhysicians() {
        return this.action.acsOpenAction(
            "Referring Doctors",
            "res.partner",
            [['is_referring_doctor', '=', true], ...this.state.domain],
            [[false, "kanban"], [false, "list"], [false, "form"]],
        );
    }

    async acsOpenAppointments() {
        return this.action.acsOpenAction(
            "Appointments",
            "hms.appointment",
            this.state.date_domain,
            [[false, "list"], [false, "kanban"], [false, "form"]],
        );
    }

    async acsOpenMyAppointments() {
        return this.action.acsOpenAction(
            "My Appointments",
            "hms.appointment",
            [['physician_id.user_id','=',user.userId], ...this.state.date_domain],
            [[false, "list"], [false, "kanban"], [false, "form"]],
        );
    }

    async acsOpenTreatments() {
        return this.action.acsOpenAction(
            "Treatments",
            "hms.treatment",
            this.state.date_domain,
            [[false, "list"], [false, "form"]],
        );
    }

    async acsOpenRunningTreatments() {
        return this.action.acsOpenAction(
            "Running Treatments",
            "hms.treatment",
            [['state','=','running'], ...this.state.date_domain],
            [[false, "list"], [false, "form"]],
        );
    }

    async acsOpenMyRunningTreatments() {
        return this.action.acsOpenAction(
            "My Running Treatments",
            "hms.treatment",
            [['state','=','running'], ['physician_id.user_id','=',user.userId], ...this.state.date_domain],
            [[false, "list"], [false, "form"]],
        );
    }
    
    async acsOpenMyTreatments() {
        return this.action.acsOpenAction(
            "My Treatments",
            "hms.treatment",
            [['physician_id.user_id','=',user.userId], ...this.state.date_domain],
            [[false, "list"], [false, "form"]],
        );
    }

    async acsOpenProcedures() {
        return this.action.acsOpenAction(
            "My Procedures",
            "acs.patient.procedure",
            this.state.date_domain,
            [[false, "list"], [false, "form"]],
        );
    }

    async acsOpenEvaluations() {
        return this.action.acsOpenAction(
            "My Evaluations",
            "acs.patient.evaluation",
            this.state.date_domain,
            [[false, "list"], [false, "form"]],
        );
    }

    async acsOpenInvoice() {
        return this.action.acsOpenAction(
            "Invoices",
            "account.move",
            [['move_type','=','out_invoice'], ['state','=','posted'], ...this.state.invoice_domain],
            [[false, "list"], [false, "form"]],
            { default_move_type: 'out_invoice' },
        );
    }

    async acsOpenPatientBirthdays() {
        const todayMonthDay = await this.action.acsInitDay()
        return this.action.acsOpenAction(
            "Today's Birthday Patients",
            "hms.patient",
            [['birthday', 'like', todayMonthDay]],
            [[false, 'kanban'], [false, "list"], [false, "form"]],
        );
    }

    async acsOpenEmployeeBirthdays() {
        const todayMonthDay = await this.action.acsInitDay()
        return this.action.acsOpenAction(
            "Employees",
            "hr.employee.public",
            [['birthday', 'like', todayMonthDay]],
            [[false, 'kanban'], [false, "list"], [false, "form"]]
        );
    }
}