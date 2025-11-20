/** @odoo-module **/

import { AcsData } from '@acs_dashboard/components/common/acs_data';
import { AcsChart } from '@acs_dashboard/components/charts/acs_chart';

const chartData = new AcsData();
const chartValue = new AcsChart();

/**
 * Appointment Bar Chart
 */
export async function renderAppointmentBarChart(container) {
    if (!container) return;
    await chartValue.acsDisposeChart(container);

    let chart = container.chart;

    if (!chart) {
        chart = await chartValue.acsCreateAm4Chart(container);
        container.chart = chart;
    }

    const result = await chartData.acsFetchChartData(
        "acs.hms.dashboard",
        "acs_appointment_bar_graph",
        "Appointment Bar Chart",
        {}
    );

    const { labels, data, tooltiptext } = result;
    chart.data = labels.map((label, index) => ({
        date: label,
        appointments: data[index],
        tooltiptext: tooltiptext[index],
    }));

    if (!chart.data.length) {
        container.innerHTML = `<p style="text-align:center; color:#888; margin-top: 20px;">
            No chart data available
        </p>`;
        return chart;
    }

    if (!chart._axesCreated) {
        const categoryAxis = await chartValue.acsCreateCategoryAxis(chart, {
            category: "date",
            location: 0,
            distance: 20,
            horizontal: "right",
            verticalCenter: "middle",
            maxWidth: 120,
            rotation: 270,
            labelColor: "#1B1833",
            visibleCount: 10,
        });

        const valueAxis = await chartValue.acsCreateValueAxis(chart, {
            minWidth: 50,
            labelColor: "#1B1833",
        });

        const series = await chartValue.acsCreateColumnSeries(chart, {
            valueY: "appointments",
            categoryX: "date",
            tooltipText: "{tooltiptext}: {appointments}",
            cornerRadiusTopLeft: 10,
            cornerRadiusTopRight: 10,
            fillOpacity: 0.8,
        });

        await chartValue.acsSetColumnHoverState(series, {
            cornerRadiusTopLeft: 0,
            cornerRadiusTopRight: 0,
            fillOpacity: 1,
        });

        chart.cursor = new am4charts.XYCursor();
        await chartValue.acsAddScrollbar(chart);

        chart._axesCreated = true;
        chart._categoryAxis = categoryAxis; // Save reference for updates
    }

    chart.updateChart = (newRecord) => {
        chart.data.push(newRecord);
        if (chart.data.length > 90) chart.data.shift();
        chart._categoryAxis.start = Math.max(0, 1 - 10 / chart.data.length);
        chart._categoryAxis.end = 1;
    };

    return chart;
}

/**
 * Patient State Bar Chart with Country Dropdown
 */
export async function renderPatientStateBarChart(container, domain = []) {
    if (!container) return;
    let chartDiv = container.querySelector(".chart-div");
    if (chartDiv) {
        await chartValue.acsDisposeChart(container);
    }

    if (!chartDiv) {
        const dropdownWrapper = document.createElement("div");
        dropdownWrapper.className = "d-flex justify-content-center px-2 mb-2";

        const dropdown = document.createElement("select");
        dropdown.className = "form-select form-select-sm";
        dropdown.style.borderRadius = "8px";
        dropdown.style.padding = "8px 12px";
        dropdown.style.border = "2px solid #007bff";
        dropdown.style.textAlignLast = "center";

        dropdown.innerHTML = `<option value="" disabled selected hidden style="color: #888; font-style: italic;">🌍 Select Country</option>`;
        dropdownWrapper.appendChild(dropdown);
        container.appendChild(dropdownWrapper);

        chartDiv = document.createElement("div");
        chartDiv.className = "chart-div";
        chartDiv.style.height = "460px";
        chartDiv.style.width = "100%";
        container.appendChild(chartDiv);

        const countries = await chartData.acsFetchChartData(
            "acs.hms.dashboard",
            "acs_get_all_countries",
            "Country Pie Chart",
            { domain: domain }
        );
        countries.forEach(country => {
            const option = document.createElement("option");
            option.value = country.id;
            option.textContent = country.name;
            dropdown.appendChild(option);
        });

        let debounceTimer;
        dropdown.addEventListener("change", () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => drawChart(parseInt(dropdown.value)), 300);
        });
    }

    let chart = chartDiv.chart;
    async function drawChart(countryId = null) {
        if (chart) {
            await chartValue.acsDisposeChart(container);
            chart = null;
        }

        chart = await chartValue.acsCreateAm4Chart(chartDiv);
        chartDiv.chart = chart;

        const data = await chartData.acsFetchChartData(
            "acs.hms.dashboard",
            "acs_patient_state_bar_graph",
            "Patient State Bar Chart",
            { country_id: countryId, domain: domain }
        );

        if (!data.length) {
            chartDiv.innerHTML = `<p style="text-align:center; color:#888; margin-top: 20px;">No chart data available</p>`;
            return chart;
        }

        chart.data = data;

        if (!chart._axesCreated) {
            const categoryAxis = await chartValue.acsCreateCategoryAxis(chart, {
                category: "category",
                location: 0,
                distance: 1,
                horizontal: "left",
                verticalCenter: "middle",
                rotation: -90,
                maxWidth: 120,
                labelColor: "#1B1833",
                visibleCount: 10
            });

            const valueAxis = await chartValue.acsCreateValueAxis(chart, {
                minWidth: 50,
                labelColor: "#1B1833"
            });

            const series = await chartValue.acsCreateColumnSeries(chart, {
                valueY: "value",
                categoryX: "category",
                tooltipText: "{category}: {valueY}",
                cornerRadiusTopLeft: 10,
                cornerRadiusTopRight: 10,
                fillOpacity: 0.8,
                strokeWidth: 0,
                useDefaultColor: false
            });

            await chartValue.acsSetColumnHoverState(series, {
                cornerRadiusTopLeft: 0,
                cornerRadiusTopRight: 0,
                fillOpacity: 1
            });

            chart.cursor = new am4charts.XYCursor();
            chart.cursor.behavior = "panX";
            chart.cursor.lineX.disabled = true;
            chart.cursor.lineY.disabled = true;

            await chartValue.acsAddScrollbar(chart);

            chart._axesCreated = true;
        }
    }
    await drawChart();
}

/**
 * Patient Disease Bar Chart
 */
export async function renderPatientDiseaseBarChart(container, domain=[]) {
    if (!container) return;
    await chartValue.acsDisposeChart(container);

    let chart = container.chart;
    if (!chart) {
        chart = await chartValue.acsCreateAm4Chart(container);
        container.chart = chart;
    }

    const result = await chartData.acsFetchChartData(
        "acs.hms.dashboard",
        "acs_appointment_disease_bar_graph",
        "Appointment Disease Bar Chart",
        { domain: domain }
    );

    const { labels, data, tooltiptext } = result;
    chart.data = labels.map((label, index) => ({
        date: label,
        appointments: data[index],
        tooltiptext: tooltiptext[index]
    }));

    if (!data.length) {
        container.innerHTML = `<p style="text-align:center; color:#888; padding-top: 100px;">No chart data available</p>`;
        return chart;
    }

    if (!chart._axesCreated) {
        const categoryAxis = await chartValue.acsCreateCategoryAxis(chart, {
            category: "date",
            location: 0,
            distance: 20,
            horizontal: "right",
            verticalCenter: "middle",
            rotation: 270,
            maxWidth: 120,
            labelColor: "#1B1833",
            visibleCount: 10
        });

        const valueAxis = await chartValue.acsCreateValueAxis(chart, {
            minWidth: 50,
            labelColor: "#1B1833"
        });

        const series = await chartValue.acsCreateColumnSeries(chart, {
            valueY: "appointments",
            categoryX: "date",
            tooltipText: "{tooltiptext}",
            cornerRadiusTopLeft: 10,
            cornerRadiusTopRight: 10,
            fillOpacity: 0.8,
            strokeWidth: 0,
            useDefaultColor: false
        });

        await chartValue.acsSetColumnHoverState(series, {
            cornerRadiusTopLeft: 0,
            cornerRadiusTopRight: 0,
            fillOpacity: 1
        });

        chart.cursor = new am4charts.XYCursor();
        await chartValue.acsAddScrollbar(chart);

        chart._axesCreated = true;
        chart._categoryAxis = categoryAxis;
    }

    chart.updateChart = (newRecord) => {
        chart.data.push(newRecord);
        chart._categoryAxis.start = Math.max(0, 1 - 10 / chart.data.length);
        chart._categoryAxis.end = 1;
    };

    return chart;
}
