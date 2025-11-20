/** @odoo-module **/

import { AcsData } from '@acs_dashboard/components/common/acs_data';
import { AcsChart } from '@acs_dashboard/components/charts/acs_chart';

const chartData = new AcsData();
const chartValue = new AcsChart();

/**
 * Patient Age Gauge Chart
 */
export async function renderPatientAgeGaugeChart(container, domain = []) {
    if (!container) return;
    await chartValue.acsDisposeChart(container);
    container.innerHTML = "";

    const response = await chartData.acsHandleRequest(
        "acs.hms.dashboard", 
        "acs_patient_age_gauge_graph", 
        [],
        { domain: domain }
    );
    const data = (typeof response.json === 'function') ? await response.json() : response;
    const rawData = data?.result ?? data;

    if (!Array.isArray(rawData) || rawData.length === 0) {
        container.innerHTML = "<p style='text-align:center; color:#888; padding-top:100px;'>No age data to display.</p>";
        return;
    }
    const total = rawData.reduce((sum, item) => sum + item.count, 0);
    const processedData = rawData.map(item => ({
        age_group: item.age_group,
        count: total > 0 ? (item.count / total) * 100 : 0,
        full: 100,
        actual_count: item.count
    }));

    const chart = await chartValue.acsCreateRadarChart(container);
    chart.data = processedData;

    await chartValue.acsCreateRadarCategoryAxis(chart);
    await chartValue.acsCreateRadarValueAxis(chart);
    await chartValue.acsCreateRadarColumnSeries(chart, {
        valueX: "full",
        categoryY: "age_group",
        fillOpacity: 0.08,
        fillColor: new am4core.InterfaceColorSet().getFor("alternativeBackground"),
        tooltipText: ""
    });
    await chartValue.acsCreateRadarColumnSeries(chart, {
        valueX: "count",
        categoryY: "age_group",
        tooltipText: "{age_group}: [bold]{valueX}[/] patients ({actual_count.formatNumber('#.#')})"
    });
    await chartValue.acsConfigureRadarCursor(chart);
    return chart;
}

/**
 * Patient Gender Pie Chart
 */
export async function renderPatientGenderPieChart(container, domain=[]) {
    if (!container) return;
    await chartValue.acsDisposeChart(container);
    container.innerHTML = "";

    const resultData = await chartData.acsFetchChartData(
        "acs.hms.dashboard", 
        "acs_patient_gender_pie_graph", 
        "Patient Gender Pie Chart",
        { domain: domain }
    );

    if (!resultData || resultData.length === 0) {
        container.innerHTML = "<p style='text-align: center; color: #888; padding-top:100px;'>No gender data to display.</p>";
        return;
    }

    const chartObj = await chartValue.acsCreatePieChart(container, async () => resultData);

    if (!chartObj || !chartObj.chart) {
        console.warn("Pie chart creation failed.");
        container.innerHTML = "<p style='text-align: center; color: #888; padding-top:100px;'>Cannot render chart.</p>";
        return;
    }

    const chart = chartObj.chart;

    chart.data = resultData.map(item => ({
        gender: item.gender,
        patient_count: item.count
    }));

    await chartValue.acsPieChartSeries(chart, "patient_count", "gender");
}

/**
 * Appointment Department Donut Char
 */
export async function renderDepartmentDonutChart(container, domain = []) {
    if (!container) return;
    await chartValue.acsDisposeChart(container);
    container.innerHTML = "";

    const data = await chartData.acsFetchChartData(
        "acs.hms.dashboard", 
        "acs_patient_depart_donut_graph",
        "Department Donut Chart",
        { domain: domain }
    );
    if (!data || data.length === 0) {
        container.innerHTML = "<p style='text-align: center; color: #888; padding-top:100px;'>No department data to display.</p>";
        return;
    }
    const chart = await chartValue.acsCreateDonutChart(container, 50);
    chart.data = data;
    await chartValue.acsDonutChartSeries(chart, "count", "department");
}

/**
 * Patient Country Pie Char
 */
export async function renderPatientCountryPieChart(container, domain=[]) {
    if (!container) return;
    await chartValue.acsDisposeChart(container);
    container.innerHTML = "";

    const resultData = await chartData.acsFetchChartData(
        "acs.hms.dashboard", 
        "acs_patient_country_pie_graph", 
        "Patient Country Data",
        { domain: domain }
    );

    if (!resultData || resultData.length === 0) {
        container.innerHTML = "<p style='text-align: center; color: #888; padding-top:100px;'>No country data to display.</p>";
        return;
    }

    const chartObj = await chartValue.acsCreatePieChart(container, async () => resultData);

    if (!chartObj || !chartObj.chart) {
        console.warn("Pie chart creation failed.");
        container.innerHTML = "<p style='text-align: center; color: #888; padding-top:100px;'>Cannot render chart.</p>";
        return;
    }

    const chart = chartObj.chart;

    const sortedTop10 = resultData
        .sort((a, b) => b.value - a.value)
        .slice(0, 10);

    chart.data = sortedTop10.map(item => ({
        country: item.category,
        patient_count: item.value,
        id: item.id
    }));

    await chartValue.acsPieChartSeries(chart, "patient_count", "country", {
        legendPosition: "left",
        legendMaxHeight: 300,
        legendMaxWidth: 250,
        legendScrollable: false,
        legendLabelWrap: true,
        legendLabelWidth: 100,
        legendFontSize: 16,
        legendMarkerSize: 16,
        legendItemPadding: 2
    });
}
