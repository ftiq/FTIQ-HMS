# MKA: Instructions for Adding Webcam View

You can enable the webcam feature by adding the below method inside your respective model.  
It will work automatically without requiring any other changes.

Example:

In Python:
------------
class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def acs_webcam_update_image(self, res_id, image_field=None, image_data=None):
        if not res_id or not image_field or not image_data:
            return False
        partner = self.env['res.partner'].sudo().search([('id', '=', res_id)], limit=1)
        if partner:
            image_fd = image_field or "image_1920"
            partner.write({image_fd: image_data})
            return True
        return False

For updating the image on any custom field,  
you can define a new image field or set a fallback in Python as shown below:

image_fd = image_field or "image_1920"

In Views:
---------
You need to add the button in your form view where desired, and call the code below according to your model and button.

<record id="acs_webcam_partner_view" model="ir.actions.client">
        <field name="name">Webcam</field>
        <field name="tag">AcsWebCam</field>
        <field name="res_model">res.partner</field>
    </record>