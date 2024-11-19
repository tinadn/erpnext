// Copyright (c) 2023, 8848 Digital LLP and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["WBS Drilldown"] = {
	"filters": [

		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd":1

		},

		

		// {
		// 	"fieldname":"project",
		// 	"label": __("Project"),
		// 	"fieldtype": "Link",
		// 	"options":'Project',
		// 	"reqd":1			
		// },

		{
			"fieldname":"project",
			"label": __("Project"),
			"fieldtype": "MultiSelectList",
			"options": "Project",
			get_data: function(txt) {
				return frappe.db.get_link_options('Project', txt, {
					is_wbs:1,
					company:frappe.query_report.get_filter_value("company")

				});
			}
		},

		{
			"fieldname":"wbs",
			"label": __("WBS"),
			"fieldtype": "Link",
			"options":'Work Breakdown Structure'
			


			
		},

		{
			"fieldname":"show_group_totals",
			"label": __("Show Group Totals"),
			"fieldtype": "Check",
			"default":1
		}

		
		

	],

	"open_budget_entry":function(data){
		if (!data.wbs) return;
		let project = $.grep(frappe.query_report.filters, function(e){ return e.df.fieldname == 'project'; });

		var only_overall_amounts = 0
		if(data.only_overall_amounts = 1){
			only_overall_amounts = 1
		}
		else{
			only_overall_amounts = 0
		}
		frappe.route_options = {
			"wbs": data.wbs,
			"company": frappe.query_report.get_filter_value('company'),
			"project": (project && project.length > 0) ? project[0].$input.val() : ""
		};

		let report = "Budget Entry";

		

		frappe.set_route("query-report", report);
	},

	"open_budget_entry2":function(data){
		if (!data.wbs) return;
		let project = $.grep(frappe.query_report.filters, function(e){ return e.df.fieldname == 'project'; });
		let group_totals = $.grep(frappe.query_report.filters, function(e){ return e.df.fieldname == 'show_group_totals'; });
		if(!project){
			project = data.project
		}

		// var html = `<p>This is a lock symbol: &#128274;</p>`
		// console.log(html)
		// var all_wbs = []
		// if(group_totals[0].value == 1){
		// 	frappe.call({
		// 		method:"project_system.project_system.report.wbs_drilldown.wbs_drilldown.get_all_wbs",
		// 		args:{
		// 			"wbs":data.wbs
		// 		},
		// 		callback:function(r){
		// 			if(r.message){
		// 				all_wbs = r.message
		// 			}
		// 			console.log("------------------------wbs34567",all_wbs)
		// 		}
		// 	})
		// }
		// else{
		// 	all_wbs = data.wbs
		// }
	
		frappe.route_options = {
			"wbs": data.wbs,
			"company": frappe.query_report.get_filter_value('company'),
			"only_overall_amounts":1,
			"show_group_totals":group_totals[0].value,
			"project": (project && project.length > 0) ? project[0].$input.val() : ""
		};

		let report = "Budget Entry";

		

		frappe.set_route("query-report", report);
	},


	"open_committed_line_items":function(data){
		if (!data.wbs) return;
		let project = $.grep(frappe.query_report.filters, function(e){ return e.df.fieldname == 'project'; });
		let group_totals = $.grep(frappe.query_report.filters, function(e){ return e.df.fieldname == 'show_group_totals'; });

		
		frappe.route_options = {
			"wbs": data.wbs,
			"show_group_totals":group_totals[0].value,
			"project": (project && project.length > 0) ? project[0].$input.val() : ""
		};

		let report = "Commited Line Item";

		

		frappe.set_route("query-report", report);
	},

	"open_actual_line_items":function(data){
		if (!data.wbs) return;
		let project = $.grep(frappe.query_report.filters, function(e){ return e.df.fieldname == 'project'; });
		let group_totals = $.grep(frappe.query_report.filters, function(e){ return e.df.fieldname == 'show_group_totals'; });

		
		frappe.route_options = {
			"wbs": data.wbs,
			"show_group_totals":group_totals[0].value,
			"project": (project && project.length > 0) ? project[0].$input.val() : ""
		};

		let report = "Actual Line Items";

		

		frappe.set_route("query-report", report);
	},

	


	"formatter": function(value, row, column, data, default_formatter) {
		const cname = ["wbs","available_budget"]
		if (data && column.fieldname == "wbs") {
			data.only_overall_amounts = 0
			value = data.wbs || value;

			column.link_onclick =
			"frappe.query_reports['WBS Drilldown'].open_budget_entry(" + JSON.stringify(data) + ")";
			column.is_tree = true;
		}

		else if (data && column.fieldname == "overall_budget") {
			
			value = value;
			console.log("----------------------------data2333",data)
			data.only_overall_amounts = 1
			column.link_onclick =
			"frappe.query_reports['WBS Drilldown'].open_budget_entry2(" + JSON.stringify(data) + ")";
			column.is_tree = true;
		}

		else if (data && column.fieldname == "committed_overall_budget") {
			
			value = value;
			column.link_onclick =
			"frappe.query_reports['WBS Drilldown'].open_committed_line_items(" + JSON.stringify(data) + ")";
			column.is_tree = true;
		}

		else if (data && column.fieldname == "actual_overall_budget") {
			
			value = value;
			column.link_onclick =
			"frappe.query_reports['WBS Drilldown'].open_actual_line_items(" + JSON.stringify(data) + ")";
			column.is_tree = true;
		}

		if (data && data.account && column.apply_currency_formatter) {
			data.currency = erpnext.get_currency(column.company_name);
		}

		value = default_formatter(value, row, column, data);
		if (data.created_from_project) {
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");

			value = $value.wrap("<p></p>").parent().html();
		}
		return value;
	},

	
};


