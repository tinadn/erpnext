# Copyright (c) 2023, 8848 Digital LLP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.accounts.report.wbs_drilldown.wbs_drilldown_methods import *
from frappe.query_builder.functions import Coalesce, Sum
# frappe-bench-postgres/apps/erpnext/erpnext/accounts/report/wbs_drilldown/wbs_drilldown.py

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    return [
        {
            "label": _("WBS Element"),
            "fieldname": "wbs",
            "fieldtype": "Link",
            "options": "Work Breakdown Structure",
            "width": 200
        },
        {
            "label": _("WBS Name"),
            "fieldname": "wbs_name",
            "fieldtype": "Data"
        },
        {
            "label": _("WBS Level"),
            "fieldname": "wbs_level",
            "fieldtype": "Data"
        },
        {
            "label": _("Created From Project"),
            "fieldname": "created_from_project",
            "fieldtype": "Check",
            "hidden": 1
        },
        {
            "label": _("Project"),
            "fieldname": "project",
            "fieldtype": "Link",
            "options": "Project",
            "width": 200
        },
        {
            "label": _("Overall Budget"),
            "fieldname": "overall_budget",
            "fieldtype": "Link",
            "options": "Work Breakdown Structure"
        },
        {
            "label": _("Committed Overall Budget"),
            "fieldname": "committed_overall_budget",
            "fieldtype": "Link",
            "options": "Work Breakdown Structure"
        },
        {
            "label": _("Actual Overall Budget"),
            "fieldname": "actual_overall_budget",
            "fieldtype": "Link",
            "options": "Work Breakdown Structure"
        },
        {
            "label": _("Assigned Overall Budget"),
            "fieldname": "assigned_overall_budget",
            "fieldtype": "Float",
            "precision": 2
        },
        {
            "label": _("Available Budget"),
            "fieldname": "available_budget",
            "fieldtype": "Float",
            "precision": 2
        }
    ]

def get_conditions(filters):
    wbs = frappe.qb.DocType("Work Breakdown Structure")
    conditions = []

    if filters.get("wbs"):
        conditions.append(wbs.name == filters.get("wbs"))

    projects = filters.get("project")
    if projects:
        if len(projects) > 1:
            conditions.append(wbs.project.isin(projects))
        else:
            conditions.append(wbs.project == projects[0])

    return conditions

def get_totals(wbs_id):
    root_wbs = frappe.get_doc("Work Breakdown Structure", wbs_id)
    totals = {
        "og_bgt": 0.0,
        "ov_bgt": 0.0,
        "cov_bgt": 0.0,
        "acov_bgt": 0.0,
        "asov_bgt": 0.0,
        "avl_bgt": 0.0
    }
    child_wbs = frappe.db.get_all("Work Breakdown Structure", {
        "lft": [">", root_wbs.get("lft")],
        "rgt": ["<", root_wbs.get("rgt")]
    }, ['name'])

    if child_wbs:
        for j in child_wbs:
            BE = frappe.qb.DocType("Budget Entry")
            query = (
                frappe.qb.from_(BE)
                .select(
                    Coalesce(Sum(BE.overall_credit - BE.overall_debit), 0.0).as_('overall_budget'),
                    Coalesce(Sum(BE.committed_overall_credit - BE.committed_overall_debit), 0.0).as_('committed_overall_budget'),
                    Coalesce(Sum(BE.actual_overall_credit - BE.actual_overall_debit), 0.0).as_('actual_overall_budget')
                )
                .where(
                    (BE.wbs == j.get("name")) &
                    ~(BE.voucher_type.isin(["Supplementary Budget", "Budget Decrease", "Budget Transfer"]))
                )
            )
            all_budget_entries = query.run(as_dict=True)

            if all_budget_entries:
                overall_budget = all_budget_entries[0].get("overall_budget")
                committed_overall_budget = all_budget_entries[0].get("committed_overall_budget")
                actual_overall_budget = all_budget_entries[0].get("actual_overall_budget")
                assigned_overall_budget = committed_overall_budget + actual_overall_budget
                available_budget = overall_budget - assigned_overall_budget

                totals["ov_bgt"] += overall_budget or 0.0
                totals["cov_bgt"] += committed_overall_budget or 0.0
                totals["acov_bgt"] += actual_overall_budget or 0.0
                totals["asov_bgt"] += assigned_overall_budget or 0.0
                totals["avl_bgt"] += available_budget or 0.0

    return totals

def get_group_wbs(filters):
    mapped_wbs = frappe._dict()
    conditions = get_conditions(filters)
    wbs = frappe.qb.DocType('Work Breakdown Structure')

    query = (
        frappe.qb.from_(wbs)
        .select(
            wbs.name, wbs.lft, wbs.rgt, wbs.parent_work_breakdown_structure.as_('parent'), 
            wbs.project, wbs.wbs_name, wbs.level, wbs.overall_budget, 
            wbs.committed_overall_budget, wbs.actual_overall_budget, 
            wbs.created_from_project, wbs.assigned_overall_budget, 
            wbs.available_budget
        )
        .where(wbs.company == filters.get("company"))
        .orderby(wbs.lft)
    )

    for condition in conditions:
        query = query.where(condition)

    all_wbs = query.run(as_dict=True)

    for d in all_wbs:
        if not filters.get("wbs"):
            if d.parent:
                mapped_wbs[d.name] = mapped_wbs.get(d.parent, 0) + 1
            else:
                mapped_wbs[d.name] = 0
        else:
            mapped_wbs[d.name] = 0

    return all_wbs, mapped_wbs

def get_data(filters):
    out = []
    applied_filters = {}

    if filters.get("project"):
        applied_filters["project"] = filters.get("project")

    if filters.get("wbs"):
        applied_filters["name"] = filters.get("wbs")

    all_wbs, mapped_wbs = get_group_wbs(filters)

    for d in all_wbs:
        row = {
            "wbs": d.name,
            'wbs_name': d.wbs_name,
            'wbs_level': d.level,
            'created_from_project': d.created_from_project,
            'project': d.project,
            'overall_budget': d.overall_budget,
            "committed_overall_budget": d.committed_overall_budget,
            "actual_overall_budget": d.actual_overall_budget,
            "assigned_overall_budget": d.assigned_overall_budget,
            "available_budget": d.available_budget,
            "indent": mapped_wbs.get(d.name),
            "parent": d.parent
        }
        out.append(row)

    if out and filters.get("show_group_totals") and not filters.get("wbs"):
        for i in out:
            if i.get("wbs") and not i.get("created_from_project"):
                totals = get_totals(i.get("wbs"))
                if totals:
                    i.update({
                        "overall_budget": i.get("overall_budget") + totals["ov_bgt"],
                        "committed_overall_budget": i.get("committed_overall_budget") + totals["cov_bgt"],
                        "actual_overall_budget": i.get('actual_overall_budget') + totals["acov_bgt"],
                        "assigned_overall_budget": i.get('assigned_overall_budget') + totals["asov_bgt"],
                        "available_budget": i.get('available_budget') + totals["avl_bgt"]
                    })

    if out:
        for i in out:
            i.update({
                "overall_budget": custom_fmt_money(i.get("overall_budget"), currency="INR"),
                "committed_overall_budget": custom_fmt_money(i.get("committed_overall_budget"), currency="INR"),
                "actual_overall_budget": custom_fmt_money(i.get('actual_overall_budget'), currency="INR"),
                "assigned_overall_budget": i.get('assigned_overall_budget'),
                "available_budget": i.get('available_budget')
            })

    return out