# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Tour(models.Model):

    _inherit = "web_tour.tour"
    _description = "Tours"

    @api.model
    def get_consumed_tours(self):
        """ Returns the list of consumed tours for the current user """
        all_consumed_tours = self.env.cr.execute("""select name from web_tour_tour group by name""")
        all_consumed_tours = self.env.cr.fetchall()
        result = []
        if all_consumed_tours:
            for e in all_consumed_tours:
                result.append(e[0])
        return result
