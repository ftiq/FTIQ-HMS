/** @odoo-module */

import { calendarView } from '@web/views/calendar/calendar_view';

import { AcsCalendarRenderer } from './calendar_renderer';

import { registry } from '@web/core/registry';

const AcsCalendarView = {
    ...calendarView,

    Renderer: AcsCalendarRenderer,
}

registry.category('views').add('acs_booking_calendar', AcsCalendarView);
