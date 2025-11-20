/** @odoo-module **/

export class AcsKpi {
    
    constructor(orm, state) {
        this.orm = orm;
        this.state = state;
    }

    async acsHandleSingleKpi(model, method, domain = [], stateKey, errorMessage) {
        try {
            const data = await this.orm.call(model, method, domain);
            this.state[stateKey] = data || 0;
        } catch (error) {
            console.error(`${errorMessage}:`, error.message || error);
        }
    }

    async acsHandleDoubleKpi(model, method, domain = [], stateKey1, stateKey2, errorMessage) {
        try {
            const data = await this.orm.call(model, method, domain);
            if (data) {
                this.state[stateKey1] = data;
                this.state[stateKey2] = data;
            }
        } catch (error) {
            console.error(`${errorMessage}:`, error.message || error);
        }
    }

    async acsInitAllSingleKpis(SINGLE_KPI_CONFIG) {
        for (const kpi of SINGLE_KPI_CONFIG) {
            try {
                const domainValue = kpi.domainKey ? this.state[kpi.domainKey] || [] : [];
                await this.acsHandleSingleKpi(
                    kpi.model,
                    kpi.method,
                    [domainValue],
                    kpi.key,
                    `Error Fetching ${kpi.key}`
                );
            } catch (error) {
                console.error(`Error fetching ${kpi.key}:`, error);
            }
        }
    }

    async acsInitAllDoubleKpis(DOUBLE_KPI_CONFIG) {
        for (const kpi of DOUBLE_KPI_CONFIG) {
            try {
                const domainValue = kpi.domainKey ? this.state[kpi.domainKey] || [] : [];
                await this.acsHandleDoubleKpi(
                    kpi.model,
                    kpi.method,
                    [domainValue],
                    kpi.keys[0],
                    kpi.keys[1],
                    `Error Fetching ${kpi.keys.join(" & ")}`
                );
            } catch (error) {
                console.error(`Error fetching ${kpi.keys.join(" & ")}:`, error);
            }
        }
    }
}
