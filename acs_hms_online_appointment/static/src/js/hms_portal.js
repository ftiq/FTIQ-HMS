/** @almightycs-module **/

import { _t } from "@web/core/l10n/translation";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AcsAppointmentBy = publicWidget.Widget.extend({
    selector: '.acs_appointment',
    events: Object.assign({}, {
        "click input[name='appointment_by']": '_acsUpdateAppointmentBy',
    }),

    async start() {
        await this._super(...arguments);
        this.$("input[name='appointment_by']").trigger('click');
    },

    _acsUpdateAppointmentBy: function (ev) {
         var appointment_by = $(ev.currentTarget);
        var $physician_datas = appointment_by.parents().find('#acs_physician_datas');
        var $department_datas = appointment_by.parents().find('#acs_department_datas');
        if (appointment_by.val()=='department') {
            $physician_datas.addClass('acs_hide');
            $department_datas.removeClass('acs_hide');
            var departments = appointment_by.parents().find('.appoint_department_panel');
            if (departments.length) {
                departments[0].click();
            }
        } else {
            $department_datas.addClass('acs_hide');
            $physician_datas.removeClass('acs_hide');
            var physicians = appointment_by.parents().find('.appoint_person_panel');
            if (physicians.length) {
                physicians[0].click();
            }
        }
    },
});

export default {
    AcsAppointmentBy: publicWidget.registry.AcsAppointmentBy,
};