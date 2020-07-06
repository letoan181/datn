# -*- coding: utf-8 -*-
from odoo import models, api


class Attachments(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=1):
        # check if hr.applicant attachment
        is_hr_applicant = 0
        current_res_id = 0
        access_rights_uid = 1
        for arg in args:
            if arg[0] == 'res_model' and arg[2] == 'hr.applicant':
                is_hr_applicant += 1
            if arg[0] == 'res_id' and arg[2] is not None and isinstance(arg[2], int) > 0:
                is_hr_applicant += 1
                current_res_id = arg[2]

        if is_hr_applicant > 1:
            self._cr.execute("""SELECT id FROM ir_attachment WHERE res_model like 'hr.applicant' and res_id=%s""",
                             (current_res_id,))
            result = self._cr.dictfetchall()
            if result and len(result) > 0:
                a = [e['id'] for e in result]
                return a
        return super(Attachments, self)._search(args, offset=offset, limit=limit, order=order,
                                                count=False, access_rights_uid=access_rights_uid)

    @api.model
    def check(self, mode, values=None):
        if self:
            self._cr.execute('SELECT res_model FROM ir_attachment WHERE id IN %s',
                             [tuple(self.ids)])
            a = self._cr.fetchone()
            if a and a[0] == 'hr.applicant':
                return
        else:
            super(Attachments, self).check(mode, values=None)
