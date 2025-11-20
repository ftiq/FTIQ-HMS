/** @odoo-module **/
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

import { AcsAction } from "./actions/acs_action"
import { AcsGroup } from "./common/acs_group"

const { Component, useState, onMounted, onWillStart } = owl;

export class AcsDashboard extends Component {

    setup() {
        this.rpc = rpc;
        this.orm = useService("orm");
        this.actionService = useService("action");

        this.state = useState({
            dashboardColor: { 'acs_dashboard_color': '#316EBF' },
            period: "Week",
        });
        
        this.action = new AcsAction(this.actionService);
        this.group = new AcsGroup(this.orm, this.state);
        
        onWillStart(async () => {
            await Promise.all([
                this.acsGetDashColor(),
            ])
        });

        onMounted(() => {
            this.acsOnChangePeriod();
        });
    }

    async acsOnChangePeriod() {
        const now = new Date();
        let startDate, endDate;
        
        if (this.state.period == 'Today') {
            startDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} 00:00:00`;
            endDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} 23:59:59`;
        } else if (this.state.period == 'Week') {
            const sixDaysAgo = new Date(now);
            sixDaysAgo.setDate(now.getDate() - 6); // changed from current day to 6 days ago
            startDate = `${sixDaysAgo.getFullYear()}-${String(sixDaysAgo.getMonth() + 1).padStart(2, '0')}-${String(sixDaysAgo.getDate()).padStart(2, '0')} 00:00:00`;
            endDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} 23:59:59`;
        } else if (this.state.period == 'Month') {
            const oneMonthAgo = new Date(now);
            oneMonthAgo.setMonth(now.getMonth() - 1); // changed from current day of month to last month
            startDate = `${oneMonthAgo.getFullYear()}-${String(oneMonthAgo.getMonth() + 1).padStart(2, '0')}-${String(oneMonthAgo.getDate()).padStart(2, '0')} 00:00:00`;
            endDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} 23:59:59`;
        } else if (this.state.period == 'Year') {
            const oneYearAgo = new Date(now);
            oneYearAgo.setFullYear(now.getFullYear() - 1); // changed from current day of year to last year
            startDate = `${oneYearAgo.getFullYear()}-${String(oneYearAgo.getMonth() + 1).padStart(2, '0')}-${String(oneYearAgo.getDate()).padStart(2, '0')} 00:00:00`;
            endDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} 23:59:59`;
        } else if (this.state.period == 'Till_Now') {
            const systemStartDate = new Date(0);
            startDate = `${systemStartDate.getFullYear()}-${String(systemStartDate.getMonth() + 1).padStart(2, '0')}-${String(systemStartDate.getDate()).padStart(2, '0')} 00:00:00`;
            endDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
        }
        return { startDate, endDate };
    }

    async acsGetDashColor() {
        try {
            const dashColorData = await this.orm.call('res.users', 'acs_get_dashboard_color', []);
            if (dashColorData && dashColorData.acs_dashboard_color) {
                this.state.dashboardColor = dashColorData.acs_dashboard_color;
            } else {
                console.warn(_t("No dashboard color returned, defaulting to black."));
                this.state.dashboardColor = '#1C67CA';
            }
        } catch (error) {
            console.error(_t("Error fetching dashboard color:"), error);
            this.state.dashboardColor = '#1C67CA';
        }
    }
}