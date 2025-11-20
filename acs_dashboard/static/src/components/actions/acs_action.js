/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";

export class AcsAction {

    constructor(actionService) {
        this.actionService = actionService;
    }

    async acsCheckDomain(domain) {
        if (!domain) {
            console.warn(_t("Domain is undefined. Setting default value."));
            return [];
        }
        return domain;
    }

    async acsHandleAction(name, model, domain, views, context={}) {
        await this.actionService.doAction({
            type: "ir.actions.act_window",
            name: _t(name),     // Name
            res_model: model,   // Model
            domain: domain,     // Domain
            views: views,       // View
            context: context    // Context
        });
    }

    async acsInitDay() {
        const today = new Date();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        const todayMonthDay = `%-${month}-${day}`;
        return todayMonthDay
    }

    async acsOpenAction(title, model, domain, views, context = {}) {
        domain = await this.acsCheckDomain(domain);
        await this.acsHandleAction(title, model, domain, views, context);
    }
} 