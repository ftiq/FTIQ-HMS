/** @odoo-module **/

export class AcsHmsDashKpi {
    constructor(state, orm) {
        this.state = state;
        this.orm = orm
    }

    async acsLoadAllKpis() {
        const { domain, date_domain, invoice_domain } = this.state;
        try {
            const data = await this.orm.call('acs.hms.dashboard', 'acs_get_kpi_full_data', [],  
                {domain: domain || [], date_domain: date_domain || [], invoice_domain: invoice_domain || []}
            );
            Object.assign(this.state, {
                totalPatients: data.dashboard.total_patient,
                totalMyPatients: data.dashboard.my_total_patients,
                totalEvaluations: data.dashboard.total_evaluations,
                totalProcedures: data.dashboard.total_procedures,
                totalPhysicians: data.dashboard.total_physician,
                totalReferringPhysicians: data.dashboard.total_referring_physician,
                totalAppointments: data.appointments.total_appointments,
                totalMyAppointments: data.appointments.my_total_appointments,
                totalTreatments: data.treatments.total_treatments,
                totalRunningTreatments: data.treatments.total_running_treatments,
                totalMyTreatments: data.treatments.my_total_treatments,
                totalMyRunningTreatments: data.treatments.my_total_running_treatments,
                totalacsOpenInvoice: data.invoices.total_open_invoice,
                totalacsOpenInvoiceAmount: data.invoices.formatted_total_open_invoice_amount,
                countPatientBirthdays: data.birthdays.count_patients_birthday,
                countEmployeeBirthdays: data.birthdays.count_employees_birthday,
            });
        } catch (err) {
            console.error("Error loading full dashboard:", err);
        }
    }
}