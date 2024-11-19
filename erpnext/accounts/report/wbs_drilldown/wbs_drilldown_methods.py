import frappe
from frappe.utils.data import cint, cstr, flt

def custom_fmt_money(
	amount: str | float | int | None,
	precision: int | None = None,
	currency: str | None = None,
	format: str | None = None,
) -> str:
	"""
	Convert to string with commas for thousands, millions etc
	"""
	number_format = format or frappe.db.get_default("number_format") or "#,###.##"
	if precision is None:
		precision = cint(frappe.db.get_default("currency_precision")) or None

	decimal_str, comma_str, number_format_precision = get_number_format_info(number_format)

	if precision is None:
		precision = number_format_precision

	if isinstance(amount, str):
		amount = flt(amount, precision)

	if amount is None:
		amount = 0

	if decimal_str:
		decimals_after = str(round(amount % 1, precision))
		parts = decimals_after.split(".")
		parts = parts[1] if len(parts) > 1 else parts[0]
		decimals = parts
		if precision > 2:
			if len(decimals) < 3:
				if currency:
					fraction = frappe.db.get_value("Currency", currency, "fraction_units", cache=True) or 100
					precision = len(cstr(fraction)) - 1
				else:
					precision = number_format_precision
			elif len(decimals) < precision:
				precision = len(decimals)

	amount = "%.*f" % (precision, round(flt(amount), precision))

	if amount.find(".") == -1:
		decimals = ""
	else:
		decimals = amount.split(".")[1]

	parts = []
	minus = ""
	if flt(amount) < 0:
		minus = "-"

	amount = cstr(abs(flt(amount))).split(".", 1)[0]

	if len(amount) > 3:
		parts.append(amount[-3:])
		amount = amount[:-3]

		val = number_format == "#,##,###.##" and 2 or 3

		while len(amount) > val:
			parts.append(amount[-val:])
			amount = amount[:-val]

	parts.append(amount)

	parts.reverse()

	amount = comma_str.join(parts) + ((precision and decimal_str) and (decimal_str + decimals) or "")
	if amount != "0":
		amount = minus + amount
		
		amount = f"{amount}"

	return amount

number_format_info = {
	"#,###.##": (".", ",", 2),
	"#.###,##": (",", ".", 2),
	"# ###.##": (".", " ", 2),
	"# ###,##": (",", " ", 2),
	"#'###.##": (".", "'", 2),
	"#, ###.##": (".", ", ", 2),
	"#,##,###.##": (".", ",", 2),
	"#,###.###": (".", ",", 3),
	"#.###": ("", ".", 0),
	"#,###": ("", ",", 0),
	"#.########": (".", "", 8),
}

def get_number_format_info(format: str) -> tuple[str, str, int]:
	return number_format_info.get(format) or (".", ",", 2)

def get_symbol(filters):
	country_code = frappe.db.get_value("Company",filters.get("company"),["default_currency"])

	return country_code	
    