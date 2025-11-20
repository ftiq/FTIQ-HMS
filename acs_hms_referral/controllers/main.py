from odoo import http
from odoo.http import request
from odoo import models, fields, api, _,Command
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
import base64

class HMSPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        Referral = request.env['hms.referral']
        if 'referral_count' in counters:
            values['referral_count'] = Referral.search_count([]) \
                if Referral.has_access('read') else 0
        return values

    @http.route(['/my/referrals', '/my/referrals/page/<int:page>'], type='http', auth="user", website=True, sitemap=False)
    def my_referrals(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        referral = request.env['hms.referral']
        if not sortby:
            sortby = 'date'

        sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        order = sortings.get(sortby, sortings['date'])['order']
        count = referral.search_count([])
 
        pager = portal_pager(
            url="/my/referrals",
            url_args={},
            total=count,
            page=page,
            step=self._items_per_page
        )
        referrals = referral.search([],
            order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'sortings': sortings,
            'sortby': sortby,
            'referrals': referrals,
            'page_name': 'referral',
            'default_url': '/my/referrals',
            'searchbar_sortings': sortings,
            'pager': pager
        })
        return request.render("acs_hms_referral.my_referrals", values)
    
    @http.route(['/acs/my/referral/create'], type='http', auth="user", website=True, sitemap=False)
    def acs_referral_form(self, **kw):
        user = request.env.user.partner_id
        referred_physicians = request.env['res.partner'].sudo().search([('is_referring_doctor', '=', True)])
        return request.render("acs_hms_referral.portal_referral_form", {'user': user, 'referred_physicians': referred_physicians})
    
    @http.route(['/my/referral/submit'], type='http', auth="public", website=True, csrf=False)
    def referral_form_submit(self, **post):
        user = request.env.user.partner_id
        vals = {
            'patient_name': post.get('patient_name'),
            'patient_dob': post.get('patient_dob') or False,
            'phone': post.get('phone'),
            'gender': post.get('gender'),
            'referred_date': post.get('referred_date') or fields.Datetime.now(),
            'referral_type': post.get('referral_type'),
            'referred_physician_id': int(post.get('referred_physician_id')) if post.get('referred_physician_id') else False,
            'referring_partner_id': int(post.get('referring_partner_id')) if post.get('referring_partner_id') else user.id,
            'description': post.get('description'),
            'state': 'active',
        }
        Patient = request.env['hms.patient'].sudo().search([
            ('gender', '=', post.get('gender')), 
            ('birthday', 'ilike', post.get('patient_dob')), 
            '|', 
            ('name', 'ilike', post.get('patient_name')), 
            ('phone', 'ilike', post.get('phone'))], limit=1)
        if Patient:
            vals['patient_id'] = Patient.id
        company = request.env.company
        if company.acs_auto_patient_creation and not Patient:
            Patient = request.env['hms.patient'].sudo().create({
                'name': post.get('patient_name'),
                'birthday': post.get('patient_dob') or False,
                'phone': post.get('phone'),
            })
            vals['patient_id'] = Patient.id
        referral = request.env['hms.referral'].sudo().create(vals)

        files = request.httprequest.files.getlist('attachments')
        Attachment = request.env['ir.attachment'].sudo()
        for file in files:
            if file:
                file_content = file.read()
                attachment = Attachment.create({
                    'name': file.filename,
                    'datas': base64.b64encode(file_content),
                    'res_model': 'hms.referral',
                    'res_id': referral.id,
                    'type': 'binary',
                })
                referral.attachment_ids = [Command.link( attachment.id)]

        return request.render("acs_hms_referral.portal_referral_thank_you", {})

    @http.route(['/acs/my/referrals/<int:referral_id>'], type='http', auth="public", website=True, sitemap=False)
    def acs_my_referral_form_data(self, referral_id=None, access_token=None, report_type=None, message=False, download=False, **kw):
        referral = request.env['hms.referral'].search([('id','=', referral_id)], limit=1,order='create_date desc')
        order_sudo = referral
        if report_type in ('html', 'pdf', 'text'):
           return self._show_report(model=order_sudo, report_type=report_type,report_ref='acs_hms_referral.action_acs_referral_report',download=download)

        values = {
            'patient': order_sudo,
            'message': message,
            'record': order_sudo,
            'action': order_sudo._get_portal_return_action(),
        }
        return request.render("acs_hms_referral.my_referral_form", values)