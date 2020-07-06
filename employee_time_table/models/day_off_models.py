import datetime

from odoo import models, fields, api


class DayOff(models.Model):
    _name = 'attendance.day.off'

    _order = 'set_day desc'
    _rec_name = 'description'
    set_day = fields.Date('Date')
    get_weekday = fields.Char(compute='get_weekdayoff', store=True)
    description = fields.Char('Description')

    _sql_constraints = [
        ('set_day', 'unique (set_day)', 'Duplicated Date !')
    ]

    @api.depends('set_day')
    def get_weekdayoff(self):
        for rec in self:
            mydate = rec.set_day
            if mydate:
                day_name = datetime.datetime.strptime(str(mydate), '%Y-%m-%d')
                rec.get_weekday = day_name.strftime("%A")
