odoo.define('base_report_to_printer.print', function(require) {
    'use strict';

    var ActionManager = require('web.ActionManager');
    var core = require('web.core');
    var framework = require('web.framework');
    var Model = require('web.Model');
    var core = require('web.core');
    var formats = require('web.formats');
    var Session = require('web.session');

    var _t = core._t;
    var Sidebar = require('web.Sidebar');

    Sidebar.include({
        init: function () {
            var self = this;
            this._super.apply(this, arguments);
            self.sections.push({
                name: 'print_direct',
                label: _t('Direct Print')
            });
            self.items['print_direct'] =  [];
            var view = self.getParent();
        },
        add_toolbar: function(toolbar) {
            var self = this;
            var _super = this._super.apply(this, arguments);
            self.add_direct_print_toolbar();
            return _super;
        },

        on_direct_print_click: function (e) {
            // Select the first list of the current (form) view
            // or assume the main view is a list view and use that
            var self = this,
                view = this.getParent();
            var selected_ids = view.get_selected_ids();

            new Model('ir.actions.report.xml')
                .call('print_action_for_report_name', [e.report_name])
                .then(function(print_action) {
                    framework.unblockUI();
                    new Model('report')
                        .call('print_document',
                              [selected_ids,
                               e.report_name,
                               ],
                              {data: {},
                               context: {},
                               })
                        .then(function(){
                            self.do_notify(_t('Printing'),
                                           _t('Document sent to the printer ') + print_action.printer_name);
                        }).fail(function() {
                            self.do_notify(_t('Error Printing'),
                                           _t('Error when sending the document to the printer ') + print_action.printer_name);
                        });
                });
            return;
        },

        add_direct_print_toolbar: function() {
            var self = this;
            self.session.user_has_group('base_report_to_printer.printing_direct_group_manager').then(function(group) {
                if (group == true) {
                    var items = self.items['print'];
                    if (items) {
                        var new_items = [];
                        for (var i = 0; i < items.length; i++) {
                            if (items[i].action.report_type == 'qweb-pdf') {
                                new_items.push({
                                    label: items[i].label,
                                    classname: 'oe_sidebar_print',
                                    report_name: items[i].action.report_name,
                                    callback: self.on_direct_print_click
                                })
                            }
                        }
                        self.add_items('print_direct', new_items);
                    }
                }

            });

        },

    });

    ActionManager.include({
        ir_actions_report_xml: function(action, options) {
            framework.blockUI();
            action = _.clone(action);
            var _t = core._t;
            var self = this;
            var _super = this._super;

            if ('report_type' in action && action.report_type === 'qweb-pdf') {
                new Model('ir.actions.report.xml')
                    .call('print_action_for_report_name', [action.report_name])
                    .then(function(print_action){
                        if (print_action && print_action.action === 'server') {
                            framework.unblockUI();
                            new Model('report')
                                .call('print_document',
                                      [action.context.active_ids,
                                       action.report_name,
                                       ],
                                      {data: action.data || {},
                                       context: action.context || {},
                                       })
                                .then(function(){
                                    self.do_notify(_t('Report'),
                                                   _t('Document sent to the printer ') + print_action.printer_name);
                                }).fail(function() {
                                    self.do_notify(_t('Report'),
                                                   _t('Error when sending the document to the printer ') + print_action.printer_name);

                                });
                        } else {
                            return _super.apply(self, [action, options]);
                        }
                    });
            } else {
                return _super.apply(self, [action, options]);
            }
        }
    });
    
});

