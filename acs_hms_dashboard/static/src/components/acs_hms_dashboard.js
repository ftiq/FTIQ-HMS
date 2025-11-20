/** @odoo-module **/
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

import { AcsDashboard } from "@acs_dashboard/components/acs_dashboard";

import { renderAppointmentBarChart, renderPatientStateBarChart, renderPatientDiseaseBarChart } from './charts/acs_bar_chart';
import { renderPatientLineChart, renderMedicalServicesLineChart } from './charts/acs_line_chart';
import { renderPatientAgeGaugeChart, renderPatientGenderPieChart, renderDepartmentDonutChart, renderPatientCountryPieChart } from './charts/acs_pie_chart';

import { AcsHmsDashKpi } from './acs_dash_kpi';
import { AcsHmsDashAction } from './acs_dash_action';
import { AcsHmsDashGroup } from './acs_dash_group';
import { AcsHmsDashTable } from './acs_dash_table';

const { onMounted, onWillStart, useRef } = owl;

export class AcsHmsDashboard extends AcsDashboard {
    //MKA: If you don't know which are props used then below line used and get all 
    // static props = {};
    static props = {
        action: { type: Object, optional: true },
        actionId: { type: Number, optional: true },
        updateActionState: { type: Function, optional: true },
        className: { type: String, optional: true },
        globalState: { type: Object, optional: true }
    };

    setup() {
        super.setup();
        Object.assign(this.state, {});

        this.dashKpi = new AcsHmsDashKpi(this.state, this.orm);
        this.dashAction = new AcsHmsDashAction(this.state, this.action || {});
        this.dashGroup = new AcsHmsDashGroup(this.orm, this.state, this.group);
        this.dashTable = new AcsHmsDashTable(this.orm, this.state, this.actionService);

        this.appointmentBarChartContainer = useRef("appointmentBarChartContainer");
        this.patientLineChartContainer = useRef("patientLineChartContainer");
        this.patientAgeGaugeChartContainer = useRef("patientAgeGaugeChartContainer");
        this.patientGenderPieChartContainer = useRef("patientGenderPieChartContainer");
        this.departmentDonutChartContainer = useRef("departmentDonutChartContainer");
        this.patientCountryPieContainer = useRef("patientCountryPieContainer");
        this.patientStateBarChartContainer = useRef("patientStateBarChartContainer");
        this.medicalServicesBarLineContainer = useRef("medicalServicesBarLineContainer");
        this.patientDiseaseBarChartContainer = useRef("patientDiseaseBarChartContainer");

        this.debounceTimeout = null;

        onWillStart(async () => {
            await this.onChangePeriod();

            await Promise.all([
                this.dashKpi.acsLoadAllKpis(),
                this.dashGroup.acsCheckAllGroups(),
                this.dashTable.getAppointmentTable(),
            ]);
        });

        onMounted(() => {
            renderAppointmentBarChart(this.appointmentBarChartContainer.el);
            renderPatientLineChart(this.patientLineChartContainer.el);
        });
    }

    async onChangePeriod() {
        clearTimeout(this.debounceTimeout);
        this.debounceTimeout = setTimeout(async () => {
            const { startDate, endDate } = await super.acsOnChangePeriod();

            this.state.domain = [['create_date', '>=', startDate], ['create_date', '<=', endDate]];
            this.state.date_domain = [['date', '>=', startDate], ['date', '<=', endDate]];
            this.state.invoice_domain = [['invoice_date', '>=', startDate], ['invoice_date', '<=', endDate]];

            console.log("\n this.state.domain -----", this.state.domain)

            await Promise.all([
                this.dashKpi.acsLoadAllKpis(),
                this.dashTable.getAppointmentTable(),
            ]);

            await Promise.all([
                renderPatientAgeGaugeChart(this.patientAgeGaugeChartContainer.el, this.state.domain),
                renderPatientGenderPieChart(this.patientGenderPieChartContainer.el, this.state.domain),
                renderDepartmentDonutChart(this.departmentDonutChartContainer.el, this.state.domain),
                renderPatientCountryPieChart(this.patientCountryPieContainer.el, this.state.domain),
                renderPatientStateBarChart(this.patientStateBarChartContainer.el, this.state.domain),
                renderMedicalServicesLineChart(this.medicalServicesBarLineContainer.el, this.state.domain),
                renderPatientDiseaseBarChart(this.patientDiseaseBarChartContainer.el, this.state.domain),
            ]);
        }, 300);
    }


    acsOpenPatients = () => this.dashAction.acsOpenPatients();
    acsOpenMyPatients = () => this.dashAction.acsOpenMyPatients();
    acsOpenPhysicians = () => this.dashAction.acsOpenPhysicians();
    acsOpenReferringPhysicians = () => this.dashAction.acsOpenReferringPhysicians();
    acsOpenAppointments = () => this.dashAction.acsOpenAppointments();
    acsOpenMyAppointments = () => this.dashAction.acsOpenMyAppointments();
    acsOpenTreatments = () => this.dashAction.acsOpenTreatments();
    acsOpenRunningTreatments = () => this.dashAction.acsOpenRunningTreatments();
    acsOpenMyTreatments = () => this.dashAction.acsOpenMyTreatments();
    acsOpenMyRunningTreatments = () => this.dashAction.acsOpenMyRunningTreatments();
    acsOpenEvaluations = () => this.dashAction.acsOpenEvaluations();
    acsOpenProcedures = () => this.dashAction.acsOpenProcedures();
    acsOpenInvoice = () => this.dashAction.acsOpenInvoice();
    acsOpenEmployeeBirthdays = () => this.dashAction.acsOpenEmployeeBirthdays();
    acsOpenPatientBirthdays = () => this.dashAction.acsOpenPatientBirthdays();
}

AcsHmsDashboard.template = "acs_hms_dashboard.AcsHmsDashboard";
registry.category("actions").add("AcsHmsDashboard", AcsHmsDashboard);