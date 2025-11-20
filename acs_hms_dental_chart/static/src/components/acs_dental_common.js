/** @odoo-module **/

export class AcsDentalCommon {
    
    constructor(state, orm, props, patient, tooth, procedure) {
        this.state = state;
        this.orm = orm;
        this.props = props;
        this.dentalPatient = patient;
        this.dentalProcedure = procedure
        this.dentalTooth = tooth
    }

    async getDentalChartColor() {
        try {
            const chartColorData = await this.orm.call('acs.hms.dental.dash', 'acs_get_dental_color', []);
            this.state.dentalChartColor = chartColorData?.acs_dental_color || '#985184';
        } catch (error) {
            console.error("Error fetching dental chart color ----- ", error);
            this.state.dentalChartColor = '#985184';
        }
    }

    async acsGetCompanyUser() {
        try {
            const currentData = await this.orm.call("acs.hms.dental.dash", "acs_get_company_user", []);
            if (currentData) {
                this.state.currentCompany = currentData['company_name'];
                this.state.currentUser = currentData['user_name'];
            }
        } catch(error) {
            console.error("Failed to fetch company & user.", error);
        }
    }

    async acsGetAgeGroup() {
        const selectionValues = await this.orm.call('acs.hms.tooth', 'acs_get_age_group', []);
        if (selectionValues) {
            //MKA: Convert the object into an array of objects with a unique key
            this.state.groupSelections = Object.entries(selectionValues).map(([key, value]) => ({key, value}));
        }
    }

    acsOpenSurfacePopup = (tooth) => {
        this.state.currentTooth = tooth;
        this.state.showSurfaceModal = true;
        if (!Array.isArray(tooth.selected_surfaces)) {
            tooth.selected_surfaces = [];
        }
    };

    acsCloseSurface = () => {
        this.state.showSurfaceModal = false;
        this.state.currentTooth = null;
    };


    acsToggleSurface = (tooth, surface) => {
        if (!Array.isArray(tooth.selected_surfaces)) {
            tooth.selected_surfaces = [];
        }
        const idx = tooth.selected_surfaces.indexOf(surface);
        if (idx === -1) {
            tooth.selected_surfaces.push(surface);
        } else {
            tooth.selected_surfaces.splice(idx, 1);
        }
        // MKA: Automatically select the tooth if surfaces selected
        tooth.selected = tooth.selected_surfaces.length > 0;
    };

    acsSaveSurface = () => {
        this.acsCloseSurface();
        const tooth = this.state.currentTooth;
        if (tooth) {
            this.state.toothData = { ...this.state.toothData }; 
        }
    };

    acsUpdateSelectedQuadrant = (quadrant) => {
        this.state.selectedQuadrant = quadrant;
        this.fetchToothData();
    };

    acsUpdateSelectedGroup = (event) => {
        this.state.selectedGroup = event.target.value || null;
        this.fetchToothData();
    };

    fetchToothData = async () => {
        const group = this.state.selectedGroup;
        const quadrant = this.state.selectedQuadrant;
        let domain = {};

        if (group) {
            domain.age_group = group;
        }
        if (quadrant && quadrant !== "all") {
            domain.quadrant = quadrant;
        }
        await this.dentalTooth.acsGetTooth(domain);
    };

    acsShowPopup(message, type="info") {
        this.state.popup.message = message;
        this.state.popup.type = type; //MKA: "success" or "error"
        this.state.popup.show = true;
    }

    acsClosePopup = () => {
        this.state.popup.show = false;
        this.state.popup.message = "";
    }

    acsAddNewProcedure = async () => {
        // Selected tooth
        const selectedTeeth = [];
        for (const quad of Object.keys(this.state.toothData)) {
            for (const tooth of this.state.toothData[quad]) {
                if (tooth.selected) selectedTeeth.push(tooth.id);
            }
        }
        // Selected surfaces (collect from popup which is selected teeth)
        const selectedSurfaces = [];
        const seenSurfaceIds = new Set();
        for (const quad of Object.keys(this.state.toothData)) {
            for (const tooth of this.state.toothData[quad]) {
                if (tooth.selected && Array.isArray(tooth.selected_surfaces)) {
                    for (const surfaceId of tooth.selected_surfaces) {
                        if (!seenSurfaceIds.has(surfaceId)) {
                            selectedSurfaces.push(surfaceId);
                            seenSurfaceIds.add(surfaceId);
                        }
                    }
                }
            }
        }       
        // Selected procedure
        const selectedProcedures = this.state.procedureData.filter(p => p.selected);

        if (this.state.isCleaningMode) {
            if (!selectedProcedures.length) {
                return this.acsShowPopup("Please select at least one procedure.", "error");
            }
        } else if (this.state.isRemoveTooth) {
            if (!selectedTeeth.length) {
                return this.acsShowPopup("Please select at least one tooth.", "error");
            }
            if (!selectedProcedures.length) {
                return this.acsShowPopup("Please select at least one procedure.", "error");
            }
        } else {
            if (!selectedTeeth.length) {
                return this.acsShowPopup("Please select at least one tooth.", "error");
            }
            if (!selectedSurfaces.length) {
                return this.acsShowPopup("Please select at least one surface.", "error");
            }
            if (!selectedProcedures.length) {
                return this.acsShowPopup("Please select at least one procedure.", "error");
            }
        }

        try {
            const { resModel, resId, patientId } = await this.dentalPatient.acsGetContextInfo();
            if (!resModel) return this.acsShowPopup("No active model found.");
            if (!resId) return this.acsShowPopup("No active id found.");
            if (!patientId) return this.acsShowPopup("No active patient found.");
           
            const procedure = selectedProcedures[0];
            const res = await this.orm.call("acs.hms.dental.dash", "acs_create_dental_procedure",
                [patientId, selectedTeeth, selectedSurfaces, procedure.id, this.state.isCleaningMode, this.state.isRemoveTooth], { resModel, resId }
            );

            if (!res.success) return this.acsShowPopup(res.error || "Failed to create procedure.", "error");
            selectedTeeth.forEach(id => {
                for (const quad of Object.keys(this.state.toothData)) {
                    for (const tooth of this.state.toothData[quad]) {
                        tooth.selected = false;
                        tooth.selected_surfaces = []; //MKA: clear the surfaces too
                    }
                }
            });

            this.state.surfaceData.forEach(s => s.selected = false);
            procedure.selected = false;
            this.acsShowPopup(`Created new Dental Procedure of ${res.procedure_name}`, "success");
            await this.dentalProcedure.acsGetDoneProcedureTable();
            await this.dentalProcedure.acsGetNewProcedureTable();
            if (this.state.isCleaningMode) this.state.isCleaningMode = false;
            if (this.state.isRemoveTooth) this.state.isRemoveTooth = false;
        } catch (error) {
            console.error("Error creating procedure ----- ", error);
            this.acsShowPopup("Failed to create procedure. See console for details.", "error");
        }
    }

    acsOpenNoteModal = (procedureId, note) => {
        this.state.currentProcedureId = procedureId;
        this.state.currentNote = note || "";
        this.state.showNoteModal = true;
    };

    acsCloseNoteModal = () => {
        this.state.showNoteModal = false;
    };

    acsSaveProcedureNote = async () => {
        try {
            await this.orm.call("acs.hms.dental.dash", "acs_update_procedure_note", [
                this.state.currentProcedureId,
                this.state.currentNote,
            ]);
            this.state.showNoteModal = false;
            await this.dentalProcedure.acsGetDoneProcedureTable();
            await this.dentalProcedure.acsGetNewProcedureTable();
        } catch (error) {
            console.error("Error saving note ----- ", error);
            this.acsShowPopup("Failed to save note.", "error");
        }
    };

    acsHandleToothClick = (tooth) => {
        if (!tooth) return;
        const pdata = this.state.patientTeethData?.[tooth.id];

        if (pdata && pdata.procedure_remove) {
            this.state.popup = {
                show: true,
                message: "This tooth has been removed. Surface selection is disabled.",
                type: "warning",
            };
            return;
        }
        if (!Array.isArray(tooth.selected_surfaces)) {
            tooth.selected_surfaces = [];
        };
        if (this.state.isCleaningMode || this.state.isRemoveTooth) {
            tooth.selected = !tooth.selected;
            tooth.selected_surfaces = [];
            this.state.toothData = { ...this.state.toothData };
        } else {
            this.acsOpenSurfacePopup(tooth);
        }
    };
}