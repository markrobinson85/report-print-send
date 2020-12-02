# -*- coding: utf-8 -*-
# Copyright (c) 2014 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, exceptions, _, api


class Report(models.Model):
    _inherit = 'report'

    def _get_report_from_name(self, cr, uid, report_name):
        """Get the first record of ir.actions.report.xml having the ``report_name`` as value for
        the field report_name.
        """
        report_obj = self.pool['ir.actions.report.xml']
        qwebtypes = ['qweb-pdf', 'qweb-html']
        if isinstance(report_name, int):
            return report_obj.browse(cr, uid, report_name)
        else:
            conditions = [('report_type', 'in', qwebtypes), ('report_name', '=', report_name)]
            idreport = report_obj.search(cr, uid, conditions)[0]
        return report_obj.browse(cr, uid, idreport)

    @api.model
    def print_document(self, record_ids, report_name, html=None, data=None):
        """ Print a document, do not return the document file """
        report = self._get_report_from_name(report_name)
        for rec in record_ids:
            document = self.with_context(must_skip_send_to_printer=True).get_pdf(
                [rec], report_name, html=html, data=data)

            behaviour = report.behaviour()[report.id]
            printer = behaviour['printer']
            if not printer:
                raise exceptions.Warning(
                    _('No printer configured to print this report.')
                )
            object_name = ''
            object = self.env[report.model].browse(rec)
            if hasattr(object, 'display_name'):
                object_name = self.env[report.model].browse(rec).display_name
            res = printer.with_context(object_name=object_name, model=report.model, res_id=rec).print_document(report, document, report.report_type)
        return res

    @api.multi
    def _can_print_report(self, behaviour, printer, document):
        """Predicate that decide if report can be sent to printer

        If you want to prevent `get_pdf` to send report you can set
        the `must_skip_send_to_printer` key to True in the context
        """
        if self.env.context.get('must_skip_send_to_printer'):
            return False
        if behaviour['action'] == 'server' and printer and document:
            return True
        return False

    @api.v7
    def get_pdf(self, cr, uid, ids, report_name, html=None,
                data=None, context=None):
        """ Generate a PDF and returns it.

        If the action configured on the report is server, it prints the
        generated document as well.
        """
        document = super(Report, self).get_pdf(cr, uid, ids, report_name,
                                               html=html, data=data,
                                               context=context)
        report = self._get_report_from_name(cr, uid, report_name)
        behaviour = report.behaviour()[report.id]
        printer = behaviour['printer']
        can_print_report = self._can_print_report(cr, uid, ids,
                                                  behaviour, printer, document,
                                                  context=context)
        if can_print_report:
            printer.print_document(report, document, report.report_type)
        return document

    @api.v8
    def get_pdf(self, docids, report_name, html=None, data=None):
        return self._model.get_pdf(self._cr, self._uid,
                                   docids, report_name,
                                   html=html, data=data, context=self._context)
