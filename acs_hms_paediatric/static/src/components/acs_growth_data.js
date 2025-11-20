/** @odoo-module **/

export class AcsPaediatricGraphData {

    constructor(patientId = null) {
        this.patientId = patientId
    }

    async acsHandleRequest(model, method, args=[], kwargs={}) {
        const response = await fetch("/web/dataset/call_kw", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    model: model,
                    method: method,
                    args: args,
                    kwargs: kwargs,
                },
                id: Math.random(),
            }),
        });
        return response
    }

    async acsHandleResponse(response, errorMessage) {
        if (!response.ok) {
            console.error(errorMessage, response.statusText);
            throw new Error(response.statusText);
        } else {
            const result = await response.json();
            return result.result;
        }
    }

    async getPaediatricGraphData(field) {
        let chartData = await this.acsHandleResponse(
            await this.acsHandleRequest("hms.patient", "acs_get_paediatric_data", [this.patientId]),
            `Failed to fetch '${field}' graph data`
        );

        chartData = chartData[field];
        //MKA: Parse string JSON into object/array
        if (typeof chartData === "string") {
            try {
                chartData = JSON.parse(chartData);
            } catch (e) {
                console.error("Failed to parse chart data JSON", e, chartData);
                return [];
            }
        }
        if (!Array.isArray(chartData)) {
            console.warn(`Graph data for field '${field}' is not an array`, chartData);
            return [];
        }
        return chartData;
    }
}
