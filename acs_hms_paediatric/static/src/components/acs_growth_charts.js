/** @odoo-module **/

import { loadJS } from "@web/core/assets";

let chartJsReady = null;
const chartRegistry = {};

async function acsEnsureChartJs() {
    if (!chartJsReady) {
        chartJsReady = loadJS("/web/static/lib/Chart/Chart.js");
    }
    await chartJsReady;
}

function acsHexToRgb(hex) {
    hex = hex.replace("#", "");
    let bigint = parseInt(hex, 16);
    let r = (bigint >> 16) & 255;
    let g = (bigint >> 8) & 255;
    let b = bigint & 255;
    return `${r},${g},${b}`;
}

function acsMakeDynamicGradient(ctx, data, baseColor, threshold = 50) {
    const maxValue = Math.max(...data);
    let intensity = Math.min(maxValue / threshold, 1);
    const rgb = acsHexToRgb(baseColor);

    let gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, `rgba(${rgb},${0.2 + 0.6 * intensity})`);
    gradient.addColorStop(1, `rgba(${rgb},0)`);
    return gradient;
}

function acsAdjustColor(hexColor, factor = 0.7, lighten = true) {
    hexColor = hexColor.replace("#", "");
    let r = parseInt(hexColor.substring(0, 2), 16);
    let g = parseInt(hexColor.substring(2, 4), 16);
    let b = parseInt(hexColor.substring(4, 6), 16);

    if (lighten) {
        r = Math.min(255, r + (255 - r) * factor);
        g = Math.min(255, g + (255 - g) * factor);
        b = Math.min(255, b + (255 - b) * factor);
    } else {
        r = Math.max(0, r * factor);
        g = Math.max(0, g * factor);
        b = Math.max(0, b * factor);
    }

    return `rgb(${r},${g},${b})`;
}

async function acsLineChartValue(chartContainer, dataMethod, baseColor, options = {}) {
    await acsEnsureChartJs();

    if (typeof chartContainer === "string") {
        chartContainer = document.getElementById(chartContainer);
    }
    if (!chartContainer) {
        console.warn("Chart container not found.");
        return;
    }

    if (chartRegistry[chartContainer.id]) {
        chartRegistry[chartContainer.id].destroy();
        delete chartRegistry[chartContainer.id];
    }

    // Clear old content
    chartContainer.innerHTML = "";

    const result = await dataMethod();
    if (!Array.isArray(result) || !result.length) {
        // Show message if no data
        const messageEl = document.createElement("div");
        messageEl.style.textAlign = "center";
        messageEl.style.padding = "20px";
        messageEl.style.color = "#888";
        messageEl.style.fontStyle = "italic";
        messageEl.textContent = `No data available for ${options.label || "this chart"}`;
        chartContainer.appendChild(messageEl);

        console.warn(`No valid data returned for chart in '${chartContainer.id}'`, result);
        return;
    }

    const canvasEl = document.createElement("canvas");
    chartContainer.appendChild(canvasEl);
    const ctx = canvasEl.getContext("2d");

    const datasets = result.map((set, index) => {
        const data = set.values.map(v => v.y);
        let color;
        if (index === 0) {
            // Normal line: original color
            color = baseColor;
        } else {
            // Child line: adjust color to differentiate
            color = acsAdjustColor(baseColor, 0.5, true); // lighten by 50%
        }

        const gradient = acsMakeDynamicGradient(ctx, data, color, options.threshold || 50);

        return {
            label: set.title,
            data: data,
            borderColor: color,
            backgroundColor: gradient,
            fill: false,
            tension: 0.4,
            pointBackgroundColor: "#fff",
            pointBorderColor: color,
            pointRadius: 3,
            pointHoverRadius: 5,
        };
    });

    const labels = result[0].values.map(v => v.x);

    const config = {
        type: options.type || "line",
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true },
                tooltip: {
                    intersect: false,
                    mode: "index",
                    callbacks: {
                        title: function (tooltipItems) {
                            return `${tooltipItems[0].label} - Month`;
                        },
                        label: function (context) {
                            return `${context.dataset.label}: ${context.formattedValue}`;
                        }
                    }
                }
            },
            scales: {
                y: { beginAtZero: true },
                x: {
                    ticks: { autoSkip: true, maxRotation: 45, minRotation: 0 }
                }
            },
        },
    };

    chartRegistry[chartContainer.id] = new Chart(ctx, config);
}

export async function acsRenderWeightChart(container, chartBackendData, baseColor) {
    await acsLineChartValue(
        container,
        () => chartBackendData.getPaediatricGraphData("patient_weight_growth"),
        baseColor,
        { threshold: 100, label: "Weight Growth" }
    );
}

export async function acsRenderHeightChart(container, chartBackendData, baseColor) {
    await acsLineChartValue(
        container,
        () => chartBackendData.getPaediatricGraphData("patient_height_growth"),
        baseColor,
        { threshold: 250, label: "Height Growth" }
    );
}

export async function acsRenderHeadChart(container, chartBackendData, baseColor) {
    await acsLineChartValue(
        container,
        () => chartBackendData.getPaediatricGraphData("patient_head_circum_graph"),
        baseColor,
        { threshold: 200, label: "Head Circumference Growth" }
    );
}