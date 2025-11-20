/** @odoo-module **/

import { AcsData } from '@acs_dashboard/components/common/acs_data';
import { AcsChart } from '@acs_dashboard/components/charts/acs_chart';

const chartData = new AcsData();
const chartValue = new AcsChart();

/**
 * Patient Line Chart
 */
export async function renderPatientLineChart(container) {
    if (!container) return;
    await chartValue.acsDisposeChart(container);

    let chart = await chartValue.acsCreateAm4Chart(container);
    container.chart = chart;

    const result = await chartData.acsFetchChartData(
        "acs.hms.dashboard",
        "acs_new_patient_line_graph",
        "Patient Line Chart",
        {}
    );

    if (!result || !result.labels || !result.data || !result.labels.length) {
        container.innerHTML = `<p style="text-align:center; color:#888; padding-top:100px;">
            No chart data available
        </p>`;
        return chart;
    }

    chart.data = result.labels.map((label, index) => ({
        date: new Date(label.raw),
        tooltipDate: label.tooltip,
        monthLabel: label.month_label,
        value: result.data[index]
    }));

    if (!chart._axesCreated) {
        const dateAxis = await chartValue.acsCreateDateAxis(chart, {
            fillColor: "#1B1833",
            timeUnit: "day",
            count: 1,
            groupData: true,
            skipEmptyPeriods: true,
            dateFormats: { month: "MMM yyyy" },
            periodChangeDateFormats: { month: "MMM yyyy" }
        });

        const valueAxis = await chartValue.acsCreateValueAxis(chart, {
            minWidth: 50,
            labelColor: "#1B1833"
        });

        const series = await chartValue.acsCreateLineSeries(chart, {
            valueY: "value",
            dateX: "date",
            tooltipText: "{tooltipDate}: {value}",
            strokeWidth: 2,
            minBulletDistance: 15,
            tooltipCornerRadius: 20
        });

        await chartValue.acsAddCircleBullet(series, {
            radius: 4,
            strokeWidth: 2,
            fillColor: "#fff",
            hoverScale: 1.3
        });

        await chartValue.acsConfigureChartCursor(chart, { xAxis: dateAxis, snapToSeries: series });
        await chartValue.acsAddScrollbar(chart);
        chart._axesCreated = true;
        chart._dateAxis = dateAxis;
    }
    return chart;
}

/**
 * Medical Services Combo Chart (Bar + Line)
 */
export async function renderMedicalServicesLineChart(container, domain = []) {
    if (!container) return;
    container.innerHTML = "";
    await chartValue.acsDisposeChart(container);

    const serviceData = await chartData.acsFetchChartData(
        "acs.hms.dashboard",
        "acs_invoice_services_bar_line_graph",
        "Medical Service Bar Line Chart",
        { domain: domain }
    );

    if (!serviceData || !serviceData.series || !serviceData.categories || !serviceData.categories.length) {
        container.innerHTML = `<p style="text-align:center; color:#888; padding-top:100px;">
            No chart data available
        </p>`;
        return;
    }

    const data = serviceData.categories.map((cat, i) => ({
        date: cat,
        totalAmount: serviceData.series.find(s => s.name === "Total Amount")?.data[i] || 0,
        totalQuantity: serviceData.series.find(s => s.name === "Total Quantity")?.data[i] || 0
    }));

    if (!data.some(d => d.totalAmount || d.totalQuantity)) {
        container.innerHTML = `<p style="text-align:center; color:#888; padding-top:100px;">
            No chart data available
        </p>`;
        return;
    }

    let chart = container.chart;
    if (!chart) {
        chart = await chartValue.acsCreateAm4Chart(container);
        container.chart = chart;
    }

    chart.data = data;

    if (!chart._axesCreated) {
        const categoryAxis = await chartValue.acsCreateCategoryAxis(chart, {
            category: "date",
            location: 0,
            distance: 50,
            horizontal: "right",
            verticalCenter: "middle",
            rotation: -90,
            maxWidth: 120,
            labelColor: "#1B1833",
            visibleCount: 10
        });

        const amountAxis = await chartValue.acsCreateValueAxis(chart, {
            minWidth: 50,
            labelColor: "#1B1833"
        });
        amountAxis.title.text = "Total Amount";

        const quantityAxis = await chartValue.acsCreateValueAxis(chart, {
            minWidth: 50,
            labelColor: "#1B1833"
        });
        quantityAxis.title.text = "Total Quantity";
        quantityAxis.renderer.opposite = true;
        quantityAxis.syncWithAxis = amountAxis;

        const amountSeries = await chartValue.acsCreateColumnSeries(chart, {
            valueY: "totalAmount",
            categoryX: "date",
            tooltipText: "{name}: [bold]{valueY}[/]",
            cornerRadiusTopLeft: 0,
            cornerRadiusTopRight: 0,
            fillOpacity: 0.7,
            strokeWidth: 0,
            useDefaultColor: true
        });
        amountSeries.yAxis = amountAxis;
        amountSeries.name = "Total Amount";

        const quantitySeries = await chartValue.acsCreateLineSeries(chart, {
            valueY: "totalQuantity",
            categoryX: "date",
            tooltipText: "{name}: [bold]{valueY}[/]",
            strokeWidth: 2
        });
        quantitySeries.yAxis = quantityAxis;
        quantitySeries.name = "Total Quantity";

        await chartValue.acsAddCircleBullet(quantitySeries, {
            radius: 4,
            strokeWidth: 2,
            fillColor: "#fff",
            hoverScale: 1.3
        });

        chart.legend = new am4charts.Legend();
        await chartValue.acsConfigureChartCursor(chart, {
            behavior: "zoomX",
            xAxis: categoryAxis
        });
        await chartValue.acsAddScrollbar(chart);

        chart._axesCreated = true;
        chart._categoryAxis = categoryAxis;
    }

    return chart;
}
