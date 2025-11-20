/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { AcsHmsEvaluation } from "@acs_hms/components/acs_hms_evaluation";
import { acsRenderHBChart, acsRenderUrineChart, acsRenderScreatinineChart } from './acs_eva_charts';
const { useRef } = owl;

patch(AcsHmsEvaluation.prototype, {
    setup() {
        super.setup();
        this.acsHbChartContainer = useRef("acsHbChartContainer");
        this.acsUrineChartContainer = useRef("acsUrineChartContainer");
        this.acsScreatinineChartContainer = useRef("acsScreatinineChartContainer");
    },

    async acsRenderAllCharts() {
        await super.acsRenderAllCharts();
        try {
            await acsRenderHBChart(
                this.acsHbChartContainer.el,
                this.state.date_domain,
                this.chartBackendData,
                this.state.evaluationChartColor
            );

            await acsRenderUrineChart(
                this.acsUrineChartContainer.el,
                this.state.date_domain,
                this.chartBackendData,
                this.state.evaluationChartColor
            );

            await acsRenderScreatinineChart(
                this.acsScreatinineChartContainer.el,
                this.state.date_domain,
                this.chartBackendData,
                this.state.evaluationChartColor
            );
        } catch (err) {
            console.error("Error rendering gynec charts:", err);
        }
    }
});

