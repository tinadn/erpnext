// Copyright (c) 2023, Extension and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Commited Line Item"] = {
	"filters": [
		{
			"fieldname":"project",
			"label": __("Project"),
			"width": "80",
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Project', txt, {
				});
			}
	},
	{
			"fieldname":"wbs",
			"label": __("WBS"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Work Breakdown Structure', txt, {
				});
			}	
		},
		{
			"fieldname":"show_group_totals",
			"label": __("Show Group Totals"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "voucher_type",
			"label": __("Voucher Type"),
			"fieldtype": "Select",
			"options": [" ","Purchase Order", "Material Request"],
			"default": " "
		},
		{
			"fieldname": "voucher_name",
			"label": __("Voucher Name"),
			"depends_on": 'eval:doc.voucher_type',
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options(frappe.query_report.get_filter_value("voucher_type"), txt, {
				});
			}
		},
		{
			"fieldname": "supplier",
			"label": __("Supplier"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Supplier', txt, {
				});
			}
		},
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Item', txt, {
				});
			}
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Item Group', txt, {
				});
			}
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
		

		value = default_formatter(value, row, column, data);
		if (data && (row[1].indent == 0 || (row[1] && row[1].content == "Total"))) {
			value = $(`<span>${value}</span>`);
			var $value = $(value).css("font-weight", "bold");
			value = $value.wrap("<p></p>").parent().html();
		}
		return value;
	},
};