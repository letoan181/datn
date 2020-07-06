from odoo import models, fields, api


class Task(models.Model):
    _inherit = 'project.task'

    name = fields.Char(string='Title', track_visibility='always', required=True, index=True, )

    def write(self, vals):
        before_encode = []
        if 'name' in vals:
            try:
                before_encode.append(vals['name'])
                vals['name'].encode('ascii')
            except UnicodeEncodeError:
                vals['name'] = vals['name'].encode('ascii', 'ignore').decode('utf-8')
                self.message_post(body="Invalid characters. Title: %s -> %s" % (
                    before_encode[0], vals['name']))
        return super(Task, self).write(vals)

    @api.model
    def create(self, vals):
        rec = super(Task, self).create(vals)
        before_encode = []
        if rec.name:
            try:
                before_encode.append(rec.name)
                rec.name.encode('ascii')
            except UnicodeEncodeError:
                rec.name = rec.name.encode('ascii', 'ignore').decode('utf-8')
                rec.message_post(body="Ignore invalid characters.")
        return rec
