# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from collections import defaultdict

import logging
_logger = logging.getLogger(__name__)

class AcsHmsDashboard(models.Model):
    _inherit = "acs.hms.dashboard"

    @api.model
    def acs_appointment_bar_graph(self, domain=None, **kwargs):
        today = fields.Date.today()
        last_month_30_days = today - timedelta(days=31)
        next_30_days = today + timedelta(days=30)

        domain = [('date', '>=', last_month_30_days), ('date', '<=', next_30_days)]

        rows = self.env['hms.appointment']._read_group(
            domain, ['date:day'], ['id:count'], order='date:day'
        )

        labels, tooltiptext, data = [], [], []
        for row in rows:
            dt, count = row
            count = count or 0
            if isinstance(dt, str):
                dt_obj = datetime.fromisoformat(dt)
            else:
                dt_obj = dt
            labels.append(dt_obj.strftime('%d %b'))
            tooltiptext.append(dt_obj.strftime('%d %b %Y'))
            data.append(count)
        return {'labels': labels, 'data': data, 'tooltiptext': tooltiptext}

    @api.model
    def acs_new_patient_line_graph(self, domain=None, **kwargs):
        # Get today's date and the start date (30 days ago)
        today = fields.Date.today()
        start_date = today - timedelta(days=365)
        domain = [('create_date', '>=', start_date.strftime('%Y-%m-%d'))]

        rows = self.env['hms.patient']._read_group(
            domain, ['create_date:day'], ['id:count'], order='create_date:day'
        )

        labels, data = [], []
        for row in rows:
            dt, count = row
            count = count or 0
            if isinstance(dt, str):
                dt_obj = datetime.fromisoformat(dt)
            else:
                dt_obj = dt
            labels.append({
                "raw": dt,
                "tooltip": dt_obj.strftime("%b %d, %Y"),
                "month_label": dt_obj.strftime("%b %Y"),
            })
            data.append(count)
        return {"labels": labels, "data": data}

    @api.model
    def acs_patient_age_gauge_graph(self, domain=None, **kwargs):
        if domain is None:
            domain = []
        company_domain = self.acs_get_company_domain() or []
        base_domain = domain + company_domain

        AGE_GROUPS = [
            {'label': '0-12 Years', 'min': 0, 'max': 12},
            {'label': '13-17 Years', 'min': 13, 'max': 17},
            {'label': '18-35 Years', 'min': 18, 'max': 35},
            {'label': '36-60 Years', 'min': 36, 'max': 60},
            {'label': '61+ Years', 'min': 61, 'max': 200},
        ]

        today = fields.Date.today()
        patient_ids = self.env['hms.patient'].search([('birthday', '!=', False)] + base_domain).ids
        if not patient_ids:
            return [{'age_group': g['label'], 'count': 0} for g in AGE_GROUPS]

        query = """
            WITH ages AS (
                SELECT EXTRACT(YEAR FROM AGE(%s, rp.birthday))::int AS age
                FROM hms_patient hp
                JOIN res_partner rp ON hp.partner_id = rp.id
                WHERE hp.id = ANY(%s)
            )
            SELECT
                CASE
                    WHEN age BETWEEN 0 AND 12 THEN '0-12 Years'
                    WHEN age BETWEEN 13 AND 17 THEN '13-17 Years'
                    WHEN age BETWEEN 18 AND 35 THEN '18-35 Years'
                    WHEN age BETWEEN 36 AND 60 THEN '36-60 Years'
                    WHEN age >= 61 THEN '61+ Years'
                END AS age_group,
                COUNT(*) AS count
            FROM ages
            GROUP BY age_group
        """
        self.env.cr.execute(query, (today, patient_ids))
        results = dict(self.env.cr.fetchall())

        return [{'age_group': g['label'], 'count': results.get(g['label'], 0)} for g in AGE_GROUPS]

    @api.model
    def acs_patient_gender_pie_graph(self, domain=None, **kwargs):
        if domain is None:
            domain = []
        company_domain = self.acs_get_company_domain() or []
        base_domain = domain + company_domain

        patient_ids = self.env['hms.patient'].search(base_domain).ids
        if not patient_ids:
            return []

        self.env.cr.execute("""
            SELECT rp.gender, COUNT(*) 
            FROM hms_patient hp
            JOIN res_partner rp ON hp.partner_id = rp.id
            WHERE hp.id = ANY(%s)
            GROUP BY rp.gender
        """, (patient_ids,))
        results = self.env.cr.fetchall()

        gender_dict = dict(self.env['res.partner']._fields['gender'].selection)
        return [{'gender': gender_dict.get(g, 'Undefined') if g else 'Undefined', 'count': c} for g, c in results]

    @api.model
    def acs_get_all_countries(self, domain=None, **kwargs):
        if domain is None:
            domain = []

        country_ids = self.env['hms.patient'].search([('country_id', '!=', False)] + domain).mapped('country_id.id')
        countries = self.env['res.country'].search_read([('id', 'in', list(set(country_ids)))], ['id', 'name'])
        return countries

    @api.model
    def acs_patient_country_pie_graph(self, domain=None, **kwargs):
        if domain is None:
            domain = []

        company_domain = self.acs_get_company_domain() or []
        base_domain = domain + company_domain

        rows = self.env['hms.patient']._read_group(
            domain=base_domain,
            groupby=['country_id'],
            aggregates=['id:count'],
            order='country_id',
        )

        data = []
        for row in rows:
            country = row[0]
            count = row[1]
            if country:
                data.append({'category': country.name, 'value': count, 'id': country.id})
            else:
                data.append({'category': 'Unknown', 'value': count, 'id': None})

        _logger.info("ACS-06 country data ----- %s", data)
        return data


    @api.model
    def acs_patient_state_bar_graph(self, country_id=None, domain=None, **kwargs):
        if domain is None:
            domain = []

        company_domain = self.acs_get_company_domain() or []
        base_domain = domain + company_domain
        if country_id:
            base_domain.append(('country_id', '=', country_id))

        rows = self.env['hms.patient']._read_group(
            domain=base_domain,
            groupby=['state_id'],
            aggregates=['id:count'],
            order='state_id',
        )

        data = []
        for row in rows:
            state = row[0]
            count = row[1]
            if state:
                data.append({'category': state.name, 'value': count})
            else:
                data.append({'category': 'Undefined (No State)', 'value': count})

        _logger.info("ACS-07 state data ----- %s", data)
        return data

    @api.model
    def acs_patient_depart_donut_graph(self, domain=None, **kwargs):
        if domain is None:
            domain = []
        company_domain = self.acs_get_company_domain() or []
        base_domain = domain + company_domain

        domain = [('department_id', '!=', False)] + base_domain
        appointments = self.env['hms.appointment'].search_read(domain, ['department_id', 'patient_id'])
        patient_department = defaultdict(set)
        for app in appointments:
            if app['department_id'] and app['patient_id']:
                patient_department[app['department_id'][0]].add(app['patient_id'][0])

        data = [{'department': self.env['hr.department'].browse(did).name, 'count': len(pids)}
                for did, pids in patient_department.items()]
        return data

    @api.model
    def acs_appointment_disease_bar_graph(self, domain=None, **kwargs):
        if domain is None:
            domain = []
        company_domain = self.acs_get_company_domain() or []
        base_domain = domain + company_domain

        appointments = self.env['hms.appointment'].search([('diseases_ids', '!=', False)] + base_domain)
        disease_count = defaultdict(int)
        for app in appointments:
            for d in app.diseases_ids:
                disease_count[d.name] += 1

        sorted_diseases = sorted(disease_count.items(), key=lambda x: x[1], reverse=True)[:10]
        labels = [n for n, _ in sorted_diseases]
        count = [v for _, v in sorted_diseases]
        tooltip = [f"{n}: {v}" for n, v in sorted_diseases]
        return {'labels': labels, 'data': count, 'tooltiptext': tooltip}

    @api.model
    def acs_invoice_services_bar_line_graph(self, domain=None, **kwargs):
        if domain is None:
            domain = []
        company_domain = self.acs_get_company_domain() or []
        base_domain = domain + company_domain

        lines = self.env['account.move.line'].search([('move_id.move_type', '=', 'out_invoice'),
                                                      ('product_id.hospital_product_type', '!=', False)] + base_domain)
        totals = defaultdict(lambda: {"amount": 0.0, "quantity": 0.0})
        for l in lines:
            totals[l.product_id.name]["amount"] += l.price_unit
            totals[l.product_id.name]["quantity"] += l.quantity

        categories = list(totals.keys())
        price_series = {"name": "Total Amount", "data": [totals[c]["amount"] for c in categories]}
        quantity_series = {"name": "Total Quantity", "data": [totals[c]["quantity"] for c in categories]}
        return {"series": [price_series, quantity_series], "categories": categories}
