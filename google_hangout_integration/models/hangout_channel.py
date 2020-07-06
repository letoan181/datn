from odoo import models, fields, api, _
from odoo.exceptions import UserError
from ..utils.google_hangout_helper import  GoogleHangoutHelper


class DocumentGeneral(models.Model):
    _name = "hangout.channel"
    _description = "Hangout Channel"

    name = fields.Char(required=True)
    link = fields.Char()
