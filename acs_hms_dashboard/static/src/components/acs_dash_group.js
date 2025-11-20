/** @odoo-module **/

export class AcsHmsDashGroup {

    constructor(orm, state) {
        this.orm = orm;
        this.state = state;
    }

    async acsCheckAllGroups() {
        try {
            const data = await this.orm.call('acs.hms.dashboard', 'acs_get_group_full_data', []);
            Object.assign(this.state, data);
        } catch (error) {
            console.error("Error fetching group checks", error);
        }
    }
}