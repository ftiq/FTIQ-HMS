from odoo import api, fields, models, _

class ACSDocument(models.Model):
    _name = 'acs.document.type'
    _description = 'Document Type'
    _order = 'sequence desc, id'

    name = fields.Char(string="Document Type", required=True)
    description = fields.Text(string="Description")
    acs_is_default = fields.Boolean(string="Default")
    sequence = fields.Integer(default=1, string='sequence', store=True)