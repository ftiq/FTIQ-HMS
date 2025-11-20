/** @odoo-module **/

export class AcsDentalPatient {

    constructor(state, orm, props) {
        this.state = state;
        this.orm = orm;
        this.props = props;
    }

    async acsGetContextInfo() {
        const resModel = this.props?.action?.res_model || this.props?.action?.context?.active_model;
        const resId = this.props?.action?.context?.active_id || this.props?.action?.context?.active_ids;

        let patientId = null;
        if (resModel === "hms.patient") {
            patientId = resId;
        } else if (["hms.appointment", "hms.treatment", "acs.patient.procedure"].includes(resModel)) {
            const [record] = await this.orm.read(resModel, [resId], ["patient_id"]);
            patientId = record?.patient_id?.[0] || null;
        }

        console.log("\n Active Model -----", resModel);
        console.log("\n Active Id -----", resId);
        console.log("\n Active Patient -----", patientId);

        return { resModel, resId, patientId };
    }

    async acsGetPatientInfo(patientId) {
        try {
            const [patient] = await this.orm.read("hms.patient", [patientId], 
                ["name","age","code","gender","phone","email","contact_address","image_1920",
                 "company_id","primary_physician_id","birthday","blood_group"]);
            
            if (patient.age != null) {
                const ageString = patient.age;
                const patientAge = parseInt(ageString, 10);

                if (patientAge >= 0 && patientAge <= 12) {
                    this.state.selectedGroup = "child";
                } else if (patientAge >= 13 && patientAge <= 19) {
                    this.state.selectedGroup = "teen";
                } else if (patientAge >= 20) {
                    this.state.selectedGroup = "adult";
                } else {
                    this.state.selectedGroup = "";
                }
            }
            
            if (patient.primary_physician_id?.length){
                const [physician] = await this.orm.read("hms.physician", [patient.primary_physician_id[0]], 
                    ["name"]);
                patient.physician_name = physician.name;
            };

            if (patient.company_id?.length) {
                const [company] = await this.orm.read("res.company", [patient.company_id[0]], 
                    ["name","logo"]);
                patient.company_name = company.name;
                patient.company_logo = company.logo;
            };
            this.state.patient = patient;
        } catch (error) {
            console.error("Failed to fetch patient data.", error);
        }
    }
}