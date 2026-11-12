# Copyright (c) 2026, Nayfaaro CRM and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


@frappe.whitelist()
def setup_realestate():
	"""
	Configures Real Estate custom fields and layout for the current tenant site
	(e.g. cuud.nayfaro.com). English language only.
	"""
	custom_fields = {
		"CRM Lead": [
			{
				"fieldname": "client_purpose",
				"label": "Purpose",
				"fieldtype": "Select",
				"options": "\nSelling Property\nBuying Property\nLooking for Rent\nOffering for Rent",
				"insert_after": "mobile_no",
				"in_list_view": 1,
				"in_standard_filter": 1,
			},
			{
				"fieldname": "property_type",
				"label": "Property Type",
				"fieldtype": "Select",
				"options": "\nLand / Plot\nHouse / Villa\nApartment\nCommercial / Office",
				"insert_after": "client_purpose",
				"in_list_view": 1,
				"in_standard_filter": 1,
			},
			{
				"fieldname": "budget_or_price",
				"label": "Budget / Price",
				"fieldtype": "Currency",
				"insert_after": "property_type",
				"in_list_view": 1,
			},
			{
				"fieldname": "preferred_location",
				"label": "Location",
				"fieldtype": "Data",
				"insert_after": "budget_or_price",
				"in_list_view": 1,
				"in_standard_filter": 1,
			},
			{
				"fieldname": "property_details",
				"label": "Property Details / Notes",
				"fieldtype": "Small Text",
				"insert_after": "preferred_location",
			},
		],
		"CRM Deal": [
			{
				"fieldname": "client_purpose",
				"label": "Deal Type",
				"fieldtype": "Select",
				"options": "\nProperty Sale\nRental",
				"insert_after": "deal_owner",
				"in_list_view": 1,
				"in_standard_filter": 1,
			},
			{
				"fieldname": "property_type",
				"label": "Property Type",
				"fieldtype": "Select",
				"options": "\nLand / Plot\nHouse / Villa\nApartment\nCommercial / Office",
				"insert_after": "client_purpose",
				"in_list_view": 1,
			},
			{
				"fieldname": "property_location",
				"label": "Location",
				"fieldtype": "Data",
				"insert_after": "property_type",
			},
		],
	}

	create_custom_fields(custom_fields, update=True)

	# Configure Quick Entry Layout for CRM Lead
	# Clean, professional Real Estate layout in English without B2B clutter
	lead_quick_entry_layout = [
		{
			"name": "contact_section",
			"columns": [
				{"name": "col_name", "fields": ["first_name", "last_name"]},
				{"name": "col_contact", "fields": ["mobile_no", "email"]},
			],
		},
		{
			"name": "property_section",
			"columns": [
				{"name": "col_purpose", "fields": ["client_purpose", "preferred_location"]},
				{"name": "col_type", "fields": ["property_type", "budget_or_price"]},
				{"name": "col_details", "fields": ["property_details"]},
			],
		},
		{
			"name": "lead_section",
			"columns": [
				{"name": "col_status", "fields": ["status"]},
				{"name": "col_owner", "fields": ["lead_owner"]},
			],
		},
	]

	layout_str = json.dumps(lead_quick_entry_layout)
	if frappe.db.exists("CRM Fields Layout", "CRM Lead-Quick Entry"):
		frappe.db.set_value("CRM Fields Layout", "CRM Lead-Quick Entry", "layout", layout_str)
	else:
		doc = frappe.new_doc("CRM Fields Layout")
		doc.name = "CRM Lead-Quick Entry"
		doc.dt = "CRM Lead"
		doc.type = "Quick Entry"
		doc.layout = layout_str
		doc.insert()

	# Update CRM Lead-Side Panel so agents see these fields when inspecting a lead
	if frappe.db.exists("CRM Fields Layout", "CRM Lead-Side Panel"):
		side_panel_doc = frappe.get_doc("CRM Fields Layout", "CRM Lead-Side Panel")
		try:
			sp_layout = json.loads(side_panel_doc.layout)
			real_estate_fields = [
				"client_purpose",
				"property_type",
				"budget_or_price",
				"preferred_location",
				"property_details",
			]
			if sp_layout and isinstance(sp_layout, list) and len(sp_layout) > 0:
				first_cols = sp_layout[0].get("columns", [])
				if first_cols:
					for field in real_estate_fields:
						if field not in first_cols[0].get("fields", []):
							first_cols[0]["fields"].append(field)
					side_panel_doc.layout = json.dumps(sp_layout)
					side_panel_doc.save()
		except Exception:
			pass

	frappe.db.commit()
	frappe.clear_cache(doctype="CRM Lead")
	frappe.clear_cache(doctype="CRM Deal")
	return "Real Estate customization applied successfully in English!"
