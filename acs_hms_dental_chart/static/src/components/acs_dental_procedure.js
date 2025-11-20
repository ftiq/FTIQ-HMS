/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";

export class AcsDentalProcedure {
    
    constructor(state, orm, actionService, patient, common) {
        this.state = state;
        this.orm = orm;
        this.actionService = actionService;
        this.dentalPatient = patient;
        this.dentalCommon = common
    }

    async acsGetProcedures() {
        try {
            const procedure = await this.orm.call("acs.hms.dental.dash", "acs_get_procedures", []);
            if (procedure) this.state.procedureData = procedure;
        } catch (error){
            console.error("Failed to fetch procedures.", error);
        }
    }

    acsSelectProcedure = (procedure) => {
        const isSelected = procedure.selected;
        this.state.procedureData.forEach(p => p.selected = false);
        procedure.selected = !isSelected;
    }

    async acsGetNewProcedureTable(offset=0, limit=20) {
        try {
            const { resModel, resId, patientId } = await this.dentalPatient.acsGetContextInfo();
            if (!patientId) return;
            const tableData = await this.orm.call("acs.hms.dental.dash", "acs_get_procedures_table", [patientId, offset, limit]);
            if (tableData) {
                this.state.proceduresTable = { new_procedures: tableData.new_procedures || [] };
            }
        } catch(error) {
            console.error("Failed to fetch new procedure table.", error);
        }
    }

    async acsGetDoneProcedureTable(offset=0, limit=20) {
        try {
            const { resModel, resId, patientId } = await this.dentalPatient.acsGetContextInfo();
            if (!patientId) return;
            const tableData = await this.orm.call("acs.hms.dental.dash", "acs_get_procedures_table", [patientId, offset, limit]);
            if (tableData) {
                this.state.proceduresDoneTable = { procedures_done: tableData.procedures_done || [] };
            }
        } catch(error) {
            console.error("Failed to fetch done procedure table.", error);
        }
    }

    async acsUpdateProcedureStatus(procedureId, state) {
        try {
            if (!procedureId || !state) return;

            const res = await this.orm.call(
                "acs.hms.dental.dash",
                "acs_update_procedure_status",
                [procedureId, state]
            );

            if (res.deleted) {
                this.dentalCommon.acsShowPopup(
                    `Procedure ${res.procedure_name} deleted successfully.`,
                    "success"
                );
            } else if (!res.success) {
                this.dentalCommon.acsShowPopup(
                    res.error || "Failed to update procedure status.",
                    "error"
                );
            }

            // Refresh your own tables
            await this.acsGetDoneProcedureTable(0, 20);
            await this.acsGetNewProcedureTable(0, 20);

        } catch (error) {
            console.error("Failed to update procedure status.", error);
            this.dentalCommon.acsShowPopup("Failed to update procedure status.", "error");
        }
    }

    async acsOpenProcedure(procedureId) {
        try {
            const result = await this.orm.call('acs.patient.procedure', 'read', [[procedureId], ['id', 'name', 'patient_id']]);
            if (result && result.length) {
                const record = result[0];
                this.actionService.doAction({
                    type: 'ir.actions.act_window',
                    name: record.name || _t('Dental Procedure'),
                    res_model: 'acs.patient.procedure',
                    res_id: procedureId,
                    views: [[false, 'form']],
                    target: 'current',
                    context: {
                        default_patient_id: record.patient_id ? record.patient_id[0] : this.state.patient.id,
                        open_from_id: this.state.patient.id,
                        open_from_model: 'hms.patient',
                    },
                });
            } else {
                console.error("No dental procedure found with this ID.");
            }
        } catch (error) {
            console.error("Error opening dental procedure record ----- ", error);
        }
    }
}