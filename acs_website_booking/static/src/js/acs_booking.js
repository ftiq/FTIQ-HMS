/** @almightycs-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AcsBookingDatePicker = publicWidget.Widget.extend({
    selector: '#ACSBookingDatePicker',

    async start() {
        await this._super(...arguments);
        this._acsLoadPicker();
    },

    _acsLoadPicker() {
        var slot_date_input = $("input[name='slot_date']");
        var last_date = $("input[name='last_date']");
        
        var disable_dates = $("input[name='disable_dates']");

        function DisableDates(date) {
            var string = jQuery.datepicker.formatDate('yy-mm-dd', date);
            return [disable_dates.val().indexOf(string) == -1];
        }
    
        var languages = document.getElementsByClassName("js_change_lang active");
        if (languages.length > 0) { 
            var lang = languages[0].getAttribute('data-url_code', '');
            if (lang.startsWith('es')) {        
                $.datepicker.regional['es'] = {
                    closeText: 'Cerrar',
                    prevText: '< Ant',
                    nextText: 'Sig >',
                    currentText: 'Hoy',
                    monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
                    monthNamesShort: ['Ene','Feb','Mar','Abr', 'May','Jun','Jul','Ago','Sep', 'Oct','Nov','Dic'],
                    dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
                    dayNamesShort: ['Dom','Lun','Mar','Mié','Juv','Vie','Sáb'],
                    dayNamesMin: ['Do','Lu','Ma','Mi','Ju','Vi','Sá'],
                    weekHeader: 'Sm',
                    dateFormat: 'mm/dd/yy',
                    firstDay: 1,
                    isRTL: false,
                    showMonthAfterYear: false,
                    yearSuffix: ''
                };
                $.datepicker.setDefaults($.datepicker.regional['es']);
            }
        }


        $("#ACSBookingDatePicker").datepicker({
            numberOfMonths: 1,
            format: 'mm/dd/yy',
            beforeShowDay: DisableDates, 
            onSelect: function(date) {
                slot_date_input.val(date);
                var records = document.getElementsByClassName("acs_booking_slot");
                var i;
                var slot_to_show = false;
                var acs_no_slots = document.getElementsByClassName("acs_no_slots");
                for (i = 0; i < records.length; i++) {
                    var rec_date = records[i].getAttribute('data-date');
                    if (date==rec_date) {
                        records[i].style.display = "";
                        slot_to_show = true;
                    } else {
                        records[i].style.display = "none";
                    }
                }
                if (slot_to_show==true) {
                    acs_no_slots[0].style.display = "none";
                } else {
                    acs_no_slots[0].style.display = "";
                }
            },
            minDate: new Date(),
            maxDate: new Date(last_date.val()),
            selectWeek: true,
            inline: true,
        });

        $('.ui-datepicker-current-day').click();
        slot_date_input.val(new Date());
    },
});

publicWidget.registry.AcsSlotSelected = publicWidget.Widget.extend({
    selector: '.acs_booking_slot',
    events: Object.assign({}, {
        "click": '_acsSelectClickedSlot',
    }),

    _acsSelectClickedSlot: function (ev) {
        const target = $(ev.currentTarget);
        const schedule_slot_input = $("input[name='schedule_slot_id']");
        const acs_slot_selected = document.getElementsByClassName("acs_slot_selected")[0];
        const acs_slot_not_selected = document.getElementsByClassName("acs_slot_not_selected")[0];
        const $each_appointment_slot = target.parents().find('.acs_booking_slot');
        $each_appointment_slot.removeClass('acs_active')
        $each_appointment_slot.removeClass('bg-primary')
        if (target.hasClass('acs_active') == true) {
            target.removeClass('acs_active');          
            target.removeClass('bg-primary')  
            schedule_slot_input.val('');
            if (typeof acs_slot_selected !== 'undefined') {
                acs_slot_selected.style.display = "none";
            }
            if (typeof acs_slot_not_selected !== 'undefined') {
                acs_slot_not_selected.style.display = "";
            }
        } else {
            target.addClass('acs_active');
            target.addClass('bg-primary');
            const slotline_id = target.data('slotline-id');
            schedule_slot_input.val(slotline_id);
            if (typeof acs_slot_selected !== 'undefined') {
                acs_slot_selected.style.display = "";
            }
            if (typeof acs_slot_not_selected !== 'undefined') {
                acs_slot_not_selected.style.display = "none";
            }
        }
    },
});
 
publicWidget.registry.AcsRecordSearch = publicWidget.Widget.extend({
    selector: '#AcsRecordSearch',
    events: Object.assign({}, {
        'keyup': '_acsSearchRecords',
    }),

    _acsSearchRecords() {
        var input, filter, records, rec, i, txtValue;
        input = document.getElementById("AcsRecordSearch");
        filter = input.value.toUpperCase();
        records = document.getElementsByClassName("acs_record_block");
        for (i = 0; i < records.length; i++) {
            rec = records[i].getElementsByClassName("acs_record_name")[0];
            txtValue = rec.textContent || rec.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                records[i].style.display = "";
            } else {
                records[i].style.display = "none";
            }
            const record_blocks = $(this).parents().find('.acs_record_panel:visible');
            if (record_blocks.length) {
                record_blocks[0].click();
            }
        }
        const search_input = document.getElementById("AcsRecordSearch");
        search_input.focus(); 
    },

});

export default {
    AcsBookingDatePicker: publicWidget.registry.AcsBookingDatePicker,
    AcsSlotSelected: publicWidget.registry.AcsSlotSelected,
    AcsRecordSearch: publicWidget.registry.AcsRecordSearch,
};
