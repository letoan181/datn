from odoo import models, fields


class AdvancedCancelReason(models.TransientModel):
    _name = 'advanced.refuse.reason'
    cancel_reason = fields.Text()

    def add_reason(self):
        request_id = self.env['advanced.request.detail'].sudo()._context.get('active_ids')
        request = self.env['advanced.request.detail'].sudo().browse(request_id[0])
        request.write({
            'cancel_reason': self.cancel_reason,
            'status': 'refuse'
        })
        permission = self.env['advanced.request.management'].sudo()
        permission.message_post(body=self.cancel_reason)
        return {'type': 'ir.actions.act_window_close'}

    def add_reason_all(self):
        request_id = self.env['advanced.request.detail'].sudo()._context.get('active_ids')
        request = self.env['advanced.request.detail'].sudo().browse(request_id[0])
        request.write({
            'cancel_reason': self.cancel_reason,
            'status': 'refuse'
        })
        return {'type': 'ir.actions.act_window_close'}
