// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Budget Entry"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project"
        },
        {
            "fieldname": "wbs",
            "label": __("WBS"),
            "fieldtype": "MultiSelectList",
            "options": "Work Breakdown Structure",
            get_data: function(txt) {
                return frappe.db.get_link_options("Work Breakdown Structure", txt, {});
            }
        },
        {
            "fieldname": "only_overall_amounts",
            "label": __("Show Only Overall Amounts"),
            "fieldtype": "Check"
        },
        {
            "fieldname": "only_committed_overall_amounts",
            "label": __("Show Only Committed Overall Amounts"),
            "fieldtype": "Check"
        },
        {
            "fieldname": "only_actual_overall_amounts",
            "label": __("Show Only Actual Overall Amounts"),
            "fieldtype": "Check"
        },
        {
            "fieldname": "show_group_totals",
            "label": __("Show Group Totals"),
            "fieldtype": "Check"
        },
        {
            "fieldname": "show_credit_debit_columns",
            "label": __("Show Credit Debit Columns"),
            "fieldtype": "Check"
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (data && (data.indent === 0.0 || (column.fieldname === "wbs" && data.wbs_name === "Total"))) {
            value = $(`<span>${value}</span>`);
            var $value = $(value).css("font-weight", "bold");
            value = $value.wrap("<p></p>").parent().html();
        }

        return value;
    }
};
