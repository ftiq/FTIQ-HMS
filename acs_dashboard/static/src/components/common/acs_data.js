/** @odoo-module **/

export class AcsData {

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
                id: Math.random(), // A unique ID for the RPC request
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

    async acsFetchChartData(model_name, method_name, chart_name, kwargs = {}) {
        const response = await this.acsHandleRequest(model_name, method_name, [], kwargs);
        const errorResponse = await this.acsHandleResponse(response, `Failed to fetch ${chart_name} data`);
        return errorResponse;
    }
}