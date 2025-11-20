/** @odoo-module **/

export class AcsDentalTooth {
    
    constructor(state, orm, patient) {
        this.state = state;
        this.orm = orm
        this.dentalPatient = patient
    }

    async acsGetTooth(domain = {}) {
        try {
            const tooth = await this.orm.call("acs.hms.dental.dash", "acs_get_tooth", [domain]);
            if (tooth) {
                const quadrants = ["upper_right", "upper_left", "lower_right", "lower_left"];
                let normalized = {};

                quadrants.forEach(q => {
                    normalized[q] = (tooth[q] || []).map((rec, idx) => ({
                        ...rec,
                        unique_key: `${q}-${rec.id}-${rec.fdi_code || ''}-${idx}`,
                    }));
                });
                this.state.toothData = normalized;
            }
        } catch (error) {
            console.error("Failed to fetch tooth.", error);
            this.state.toothData = {upper_right: [], upper_left: [], lower_right: [], lower_left: []};
        }
    }

    async acsGetSurfaces() {
        try {
            const surface = await this.orm.call("acs.hms.dental.dash", 'acs_get_surfaces', []);
            if (surface) this.state.surfaceData = surface;
        } catch(error) {
            console.error("Failed to fetch surfaces.", error);
        }
    }

    async acsGetPatientTeethData() {
        const { resModel, resId, patientId } = await this.dentalPatient.acsGetContextInfo();
        if (!patientId) return;
        
        try {
            const data = await this.orm.call("hms.patient","acs_get_patient_teeth_data",[patientId]);
            Object.keys(data).forEach(toothId => {
                if (data[toothId].procedure_details) {
                    let cleanText = data[toothId].procedure_details
                        .replace(/<[^>]+>/g, '')        // remove all HTML tags
                        .replace(/&#13;/g, '\n')        // convert line breaks
                        .replace(/\s+/g, ' ')           // cleanup spacing
                        .trim();
                    data[toothId].procedure_details = cleanText;
                }
            });
            this.state.patientTeethData = data || {};
        } catch(error) {
            console.error("Failed to fetch patient teeth data -----", error);
        }
    }
}