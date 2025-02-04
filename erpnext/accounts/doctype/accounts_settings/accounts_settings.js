// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Accounts Settings", {
	refresh: function (frm) {},
	enable_immutable_ledger: function (frm) {
		if (!frm.doc.enable_immutable_ledger) {
			return;
		}

		let msg = __("Enabling this will change the way how cancelled transactions are handled.");
		msg += " ";
		msg += __("Please enable only if the understand the effects of enabling this.");
		msg += "<br>";
		msg += __("Do you still want to enable immutable ledger?");

		frappe.confirm(
			msg,
			() => {},
			() => {
				frm.set_value("enable_immutable_ledger", 0);
			}
		);
	},
});


frappe.ui.form.on('Accounts Settings', {
    onload: function(frm) {
        frm.set_df_property('acc_frozen_upto', 'hidden', true);
        frm.set_df_property('frozen_accounts_modifier', 'hidden', true);
		// frm.set_df_property('ignore_account_closing_balance', 'hidden', true);

		
    }
});
