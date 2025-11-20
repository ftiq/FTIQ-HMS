/** @odoo-module **/

export class AcsGroup {
    constructor(orm, state) {
        this.orm = orm;
        this.state = state;
    }

    async acsInitGroup(cfg) {
        try {
            const result = await this.orm.call(cfg.model, cfg.method, []);
            if (result) {
                this.state[cfg.key] = result;
            }
            return result;
        } catch (error) {
            console.error(_t(`Error checking ${cfg.key}:`), error);
            return null;
        }
    }

    async acsInitAllGroups(cfgs) {
        await Promise.all(cfgs.map(cfg => this.acsInitGroup(cfg)));
    }
}