/** @odoo-module **/

import { registry } from "@web/core/registry";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

import { acsRenderWeightChart, acsRenderHeightChart, acsRenderHeadChart} from "./acs_growth_charts";
import { AcsPaediatricGraphData } from './acs_growth_data';

import { AcsDashChartColor } from "@acs_hms/components/acs_hms_evaluation" 

const { Component, useSubEnv, useState, onWillStart, onMounted, useRef } = owl;

export class AcsHmsPaediatric extends Component {

    setup() {
        this.rpc = rpc;
        this.actionService = useService("action");
        this.orm = useService("orm");

        this.acsWeightChartContainer = useRef("acsWeightChartContainer");
        this.acsHeightChartContainer = useRef("acsHeightChartContainer");
        this.acsHeadChartContainer = useRef("acsHeadChartContainer");

        this.state = useState({
            paediatricChartColor: '#985184',
        });

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });

        onWillStart(async () => {
            const patientId = await this.acsGetPatientId();
            this.chartBackendData = new AcsPaediatricGraphData(patientId);

            const AcsChartColor = AcsDashChartColor(this.orm);
            const dashChart = new AcsChartColor();
            this.state.paediatricChartColor = await dashChart.acsGetChartColor();
        });

        onMounted(() => {
            this.acsRenderAllCharts();
        });
    }

    async acsGetPatientId() {
        const patientId = this.props?.action?.context?.active_id
        console.log("\n patientId -----", patientId)
        return patientId;
    }

    async acsRenderAllCharts() {
        try {
            await acsRenderWeightChart(
                this.acsWeightChartContainer.el, 
                this.chartBackendData, 
                this.state.paediatricChartColor
            );

            await acsRenderHeightChart(
                this.acsHeightChartContainer.el, 
                this.chartBackendData, 
                this.state.paediatricChartColor
            );

            await acsRenderHeadChart(
                this.acsHeadChartContainer.el, 
                this.chartBackendData, 
                this.state.paediatricChartColor
            );
        } catch (err) {
            console.error("Error rendering charts:", err);
        }
    }
}

AcsHmsPaediatric.template = "acs_hms.AcsHmsPaediatricChart";
registry.category("actions").add("AlmightyHmsPaediatric", AcsHmsPaediatric);
