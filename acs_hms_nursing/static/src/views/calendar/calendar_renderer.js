/** @odoo-module */

import { CalendarRenderer } from '@web/views/calendar/calendar_renderer';

import { AcsCalendarCommonRenderer } from './common/calendar_common_renderer';


export class AcsCalendarRenderer extends CalendarRenderer {
    //static template = "web.CalendarRenderer";
    static components = {
        ...AcsCalendarRenderer.components,
        day: AcsCalendarCommonRenderer,
        week: AcsCalendarCommonRenderer,
        month: AcsCalendarCommonRenderer,
    };
    
}
