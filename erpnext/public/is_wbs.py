# apps/erpnext/erpnext/public/is_wbs.py

import frappe
from frappe import _

def on_update(doc, method):
    if doc.is_wbs:
        existing_wbs = frappe.get_all('Work Breakdown Structure', filters={'project': doc.name}, fields=['name'])
        
        if existing_wbs:
            return

        wbs_name = f"{doc.naming_series}{doc.name}"

        data = frappe.get_doc({
            "doctype": "Work Breakdown Structure",
            "project": doc.name,
            "project_name": doc.project_name,
            "project_type": doc.project_type,
            "company": doc.company,
            "owner": doc.owner,
            "wbs_name": doc.project_name,  
            "wbs_level": 0, 
            "description": doc.get("description"),
            "status": "Active",
            "is_group": 1 ,
            
        })
        

        try:
            data.insert(ignore_permissions=True)
        except Exception as e:
            frappe.throw(_("Error while saving WBS: {0}").format(str(e)))
