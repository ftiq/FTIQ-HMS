# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _, fields
from odoo.exceptions import ValidationError, UserError

class ACSSuregeryReport(models.AbstractModel):
    _name = 'report.acs_hms_operation_theater.report_acs_hms_surgery'
    _description = "ACS Surgery Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        start_date = data.get('form', {}).get('start_date', False)
        end_date = data.get('form', {}).get('end_date', False)
        ot_id = data.get('form', {}).get('ot_id', False)

        surgeries = self.env['hms.surgery'].search([
            ('start_date','>=',start_date),
            ('start_date','<=',end_date),
            ('hospital_ot_id','=', ot_id)
        ])
        if not surgeries:
            raise UserError(_('No Surgery to print for selected criteria.'))
        
        user_tz = self.env.user.tz or 'UTC'
        now_utc = fields.Datetime.now()
        now_local = fields.Datetime.context_timestamp(self.with_context(tz=user_tz), now_utc)

        return {
            'doc_ids': data.get('ids', data.get('active_ids')),
            'doc_model': 'hms.surgery',
            'docs': surgeries[0],
            'data': dict(
                data,
                start_date=start_date,
                end_date=end_date,
                ot_id=ot_id,
                print_date=now_local.strftime("%Y-%m-%d %I:%M:%S %p") if now_local else '',
                surgeries=surgeries,
            ),
        }
