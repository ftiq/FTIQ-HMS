/** @odoo-module */
 
import { CalendarCommonRenderer } from '@web/views/calendar/calendar_common/calendar_common_renderer';
import { AcsCalendarCommonPopover } from './calendar_common_popover';


export class AcsCalendarCommonRenderer extends CalendarCommonRenderer {
    static components = {
        ...AcsCalendarCommonRenderer,
        Popover: AcsCalendarCommonPopover,
    };
}
