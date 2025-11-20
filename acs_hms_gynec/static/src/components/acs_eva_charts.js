/** @odoo-module **/
import { acsLineChartValue } from '@acs_hms/components/acs_eva_charts';

export async function acsRenderHBChart(container, domain, chartBackendData, evaluationChartColor) {
    await acsLineChartValue(
        container,
        () => chartBackendData.getEvolutionGraphData("hb", "", domain),
        { label: "Hemoglobin (HB)", color: evaluationChartColor || "#985184", threshold: 20 }
    );
}

export async function acsRenderUrineChart(container, domain, chartBackendData, evaluationChartColor) {
    await acsLineChartValue(
        container,
        () => chartBackendData.getEvolutionGraphData("urine", "", domain),
        { label: "Urine", color: evaluationChartColor || "#985184", threshold: 10 }
    );
}

export async function acsRenderScreatinineChart(container, domain, chartBackendData, evaluationChartColor) {
    await acsLineChartValue(
        container,
        () => chartBackendData.getEvolutionGraphData("screatinine", "", domain),
        { label: "Screatinine", color: evaluationChartColor || "#985184", threshold: 10 }
    );
}
