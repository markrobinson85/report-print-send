# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Camptocamp (<http://www.camptocamp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class ResUsers(models.Model):
    _inherit = "res.users"

    printer_tray_id = fields.Many2one(
        comodel_name='printing.tray',
        string='Default Printer Paper Source',
        domain="[('printer_id', '=', printing_printer_id)]",
    )

    def __init__(self, pool, cr):
        init_res = super(ResUsers, self).__init__(pool, cr)

        self.SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        self.SELF_WRITEABLE_FIELDS.extend(['printer_tray_id'])

        self.SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        self.SELF_READABLE_FIELDS.extend(['printer_tray_id'])

        return init_res

    @api.onchange('printing_printer_id')
    def onchange_printing_printer_id(self):
        """ Reset the tray when the printer is changed """
        self.printer_tray_id = False
