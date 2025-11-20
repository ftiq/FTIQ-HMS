/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

const { Component, useState, onWillStart } = owl;

import { AcsDentalPatient } from "./acs_dental_patient";
import { AcsDentalTooth } from "./acs_dental_tooth";
import { AcsDentalProcedure } from "./acs_dental_procedure";
import { AcsDentalCommon } from "./acs_dental_common";

export class AcsHmsDentalNoteModal extends Component {
    static props = { "*": { optional: true } };
}
AcsHmsDentalNoteModal.template = "acs_hms_dental_chart.AcsHmsDentalNoteModal";

export class AcsHmsToothSurfaceModal extends Component {
    static props = { "*": { optional: true } };
}

AcsHmsToothSurfaceModal.template = "acs_hms_dental_chart.AcsHmsToothSurfaceModal";

export class AcsHmsDentalChart extends Component {
    static props = { "*": { optional: true } };
    
    setup() {
        this.rpc = rpc;
        this.action = useService("action");
        this.orm = useService("orm");
        this.actionService = useService("action");
        
        this.state = useState({
            patient: {},
            toothData: {},
            surfaceData: {},
            currentCompany: null,
            currentUser: null,
            selectedQuadrant: "all",
            procedureData: [],
            patientTeethData: [],
            searchText: "",
            proceduresTable: { new_procedures: [] },
            proceduresDoneTable: { procedures_done: [] },
            dentalChartColor: { 'acs_dental_color': '#985184' },
            // patientTeethData: {},
            
            showNoteModal: false,
            currentNote: "",
            currentProcedureId: null,
            
            popup: {
                show: false,
                message: "",
                type: "info"
            },

            groupSelections: [],
            selectedGroup: "",
            isCleaningMode: false,
            isRemoveTooth: false,
        });

        this.dentalPatient = new AcsDentalPatient(this.state, this.orm, this.props);
        this.dentalTooth = new AcsDentalTooth(this.state, this.orm, this.dentalPatient);
        this.dentalCommon = new AcsDentalCommon(
            this.state, this.orm, this.props, this.dentalPatient, this.dentalTooth, null, this.actionService
        );
        this.dentalProcedure = new AcsDentalProcedure(
            this.state, this.orm, this.actionService, this.dentalPatient, this.dentalCommon
        );
        this.dentalCommon.dentalProcedure = this.dentalProcedure;

        /*
            Bind or forward some methods from common to this component,
            so template can call them easily.        
        */
        this.fetchToothData = this.dentalCommon.fetchToothData.bind(this.dentalCommon);
        this.UpdateSelectedQuadrant = this.dentalCommon.acsUpdateSelectedQuadrant.bind(this.dentalCommon);
        this.updateSelectedGroup = this.dentalCommon.acsUpdateSelectedGroup.bind(this.dentalCommon);
        this.openSurface = this.dentalCommon.acsOpenSurfacePopup.bind(this.dentalCommon);
        this.saveSurface = this.dentalCommon.acsSaveSurface.bind(this.dentalCommon);
        this.closeSurface = this.dentalCommon.acsCloseSurface.bind(this.dentalCommon);
        this.closeNoteModal = this.dentalCommon.acsCloseNoteModal.bind(this.dentalCommon);
        this.saveProcedureNote = this.dentalCommon.acsSaveProcedureNote.bind(this.dentalCommon);
        this.toggleSurface = this.dentalCommon.acsToggleSurface.bind(this.dentalCommon);
        this.addNewProcedure = this.dentalCommon.acsAddNewProcedure.bind(this.dentalCommon);
        this.handleToothClick = this.dentalCommon.acsHandleToothClick.bind(this.dentalCommon)

        onWillStart(async () => {
            const { resModel, resId, patientId } = await this.dentalPatient.acsGetContextInfo();

            await Promise.all([
                this.dentalPatient.acsGetPatientInfo(patientId),
                this.dentalTooth.acsGetPatientTeethData(patientId),
                this.dentalCommon.getDentalChartColor(),
                this.dentalCommon.acsGetCompanyUser(),
                this.dentalCommon.acsGetAgeGroup(),
                this.dentalTooth.acsGetSurfaces(),
                this.dentalProcedure.acsGetProcedures(),
                this.dentalProcedure.acsGetDoneProcedureTable(0, 20),
                this.dentalProcedure.acsGetNewProcedureTable(0, 20),
            ]);
            await this.fetchToothData();
        });
    }

    acsGoBackToPatient() {
        history.back();
    }
}

AcsHmsDentalChart.components = { AcsHmsDentalNoteModal, AcsHmsToothSurfaceModal };
AcsHmsDentalChart.template = "acs_hms_dental_chart.AcsHmsDentalChart";
registry.category("actions").add("AcsHmsDental", AcsHmsDentalChart);