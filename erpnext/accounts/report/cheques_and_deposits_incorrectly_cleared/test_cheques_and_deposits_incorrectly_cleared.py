import unittest
from unittest.mock import patch, MagicMock
import frappe
from frappe.tests.utils import FrappeTestCase
from datetime import date, datetime

# Import the module being tested
from erpnext.accounts.report.cheques_and_deposits_incorrectly_cleared.cheques_and_deposits_incorrectly_cleared import (
    execute,
    build_payment_entry_dict,
    build_journal_entry_dict,
    build_data,
    get_amounts_not_reflected_in_system_for_bank_reconciliation_statement,
    get_columns
)


class TestChequesAndDepositsIncorrectlyCleared(FrappeTestCase):
    
    def setUp(self):
        self.filters = frappe._dict({
            'account': 'Test Bank Account - TC',
            'report_date': '2024-01-31'
        })
        
        self.sample_payment_entry = frappe._dict({
            'doctype': 'Payment Entry',
            'name': 'PE-00001',
            'posting_date': '2024-02-01',
            'clearance_date': '2024-01-30',
            'amount': 1000.0,
            'payment_type': 'Receive',
            'party_type': 'Customer'
        })
        
        self.sample_journal_entry = frappe._dict({
            'doctype': 'Journal Entry',
            'name': 'JE-00001',
            'posting_date': '2024-02-01',
            'clearance_date': '2024-01-30',
            'debit_in_account_currency': 500.0,
            'credit_in_account_currency': 0.0
        })

    # def test_get_columns(self):
    #     """Test the get_columns function returns correct column structure"""
    #     columns = get_columns()
        
    #     # Check that we get the expected number of columns
    #     self.assertEqual(len(columns), 6)
        
    #     # Check specific column properties
    #     expected_fieldnames = [
    #         'payment_document', 'payment_entry', 'debit', 
    #         'credit', 'posting_date', 'clearance_date'
    #     ]
        
    #     actual_fieldnames = [col['fieldname'] for col in columns]
    #     self.assertEqual(actual_fieldnames, expected_fieldnames)
        
    #     # Check specific column types
    #     self.assertEqual(columns[0]['fieldtype'], 'Data')
    #     self.assertEqual(columns[1]['fieldtype'], 'Dynamic Link')
    #     self.assertEqual(columns[2]['fieldtype'], 'Currency')
    #     self.assertEqual(columns[3]['fieldtype'], 'Currency')

    def test_build_payment_entry_dict_receive_customer(self):
        result = build_payment_entry_dict(self.sample_payment_entry)
        
        expected = {
            'payment_document': 'Payment Entry',
            'payment_entry': 'PE-00001',
            'posting_date': '2024-02-01',
            'clearance_date': '2024-01-30',
            'debit': 1000.0,
            'credit': 0
        }
        
        for key, value in expected.items():
            self.assertEqual(result[key], value)

    def test_build_payment_entry_dict_payment(self):
        payment_data = self.sample_payment_entry.copy()
        payment_data.payment_type = 'Pay'
        
        result = build_payment_entry_dict(payment_data)
        
        self.assertEqual(result['debit'], 0)
        self.assertEqual(result['credit'], 1000.0)

    def test_build_payment_entry_dict_receive_non_customer(self):
        payment_data = self.sample_payment_entry.copy()
        payment_data.party_type = 'Employee'
        
        result = build_payment_entry_dict(payment_data)
        
        self.assertEqual(result['debit'], 0)
        self.assertEqual(result['credit'], 1000.0)

    def test_build_journal_entry_dict(self):
        result = build_journal_entry_dict(self.sample_journal_entry)
        
        expected = {
            'payment_document': 'Journal Entry',
            'payment_entry': 'JE-00001',
            'posting_date': '2024-02-01',
            'clearance_date': '2024-01-30',
            'debit': 500.0,
            'credit': 0.0
        }
        
        for key, value in expected.items():
            self.assertEqual(result[key], value)

    @patch('erpnext.accounts.report.cheques_and_deposits_incorrectly_cleared.cheques_and_deposits_incorrectly_cleared.get_amounts_not_reflected_in_system_for_bank_reconciliation_statement')
    def test_build_data(self, mock_get_amounts):
        mock_get_amounts.return_value = [
            self.sample_payment_entry,
            self.sample_journal_entry
        ]
        result = build_data(self.filters)
        self.assertEqual(len(result), 2)
        
        self.assertEqual(result[0]['payment_document'], 'Payment Entry')
        self.assertEqual(result[0]['debit'], 1000.0)
        
        self.assertEqual(result[1]['payment_document'], 'Journal Entry')
        self.assertEqual(result[1]['debit'], 500.0)

    # @patch('erpnext.accounts.report.cheques_and_deposits_incorrectly_cleared.cheques_and_deposits_incorrectly_cleared.build_data')
    # @patch('erpnext.accounts.report.cheques_and_deposits_incorrectly_cleared.cheques_and_deposits_incorrectly_cleared.get_columns')
    # def test_execute(self, mock_get_columns, mock_build_data):
    #     # Mock the functions
    #     mock_columns = [{'fieldname': 'test', 'label': 'Test'}]
    #     mock_data = [{'test': 'value'}]
        
    #     mock_get_columns.return_value = mock_columns
    #     mock_build_data.return_value = mock_data
        
    #     columns, data = execute(self.filters)
        
    #     # Verify the functions were called
    #     mock_get_columns.assert_called_once()
    #     mock_build_data.assert_called_once_with(self.filters)
        
    #     # Verify return values
    #     self.assertEqual(columns, mock_columns)
    #     self.assertEqual(data, mock_data)

    # @patch('frappe.qb')
    # def test_get_amounts_query_structure(self, mock_qb):
    #     """Test that the database query is constructed correctly"""
    #     # Mock the query builder components
    #     mock_doctype = MagicMock()
    #     mock_qb.DocType.return_value = mock_doctype
        
    #     mock_query = MagicMock()
    #     mock_qb.from_.return_value = mock_query
        
    #     # Chain the query methods
    #     mock_query.inner_join.return_value = mock_query
    #     mock_query.on.return_value = mock_query
    #     mock_query.select.return_value = mock_query
    #     mock_query.where.return_value = mock_query
    #     mock_query.run.return_value = []
        
    #     # Call the function
    #     result = get_amounts_not_reflected_in_system_for_bank_reconciliation_statement(self.filters)
        
    #     # Verify query building was attempted
    #     self.assertTrue(mock_qb.DocType.called)
    #     self.assertTrue(mock_qb.from_.called)

    def test_build_data_empty_vouchers(self):
        with patch('erpnext.accounts.report.cheques_and_deposits_incorrectly_cleared.cheques_and_deposits_incorrectly_cleared.get_amounts_not_reflected_in_system_for_bank_reconciliation_statement') as mock_get_amounts:
            mock_get_amounts.return_value = []
            
            result = build_data(self.filters)
            
            self.assertEqual(result, [])

    def test_build_data_unknown_doctype(self):
        unknown_voucher = frappe._dict({
            'doctype': 'Unknown Type',
            'name': 'UK-00001'
        })
        
        with patch('erpnext.accounts.report.cheques_and_deposits_incorrectly_cleared.cheques_and_deposits_incorrectly_cleared.get_amounts_not_reflected_in_system_for_bank_reconciliation_statement') as mock_get_amounts:
            mock_get_amounts.return_value = [unknown_voucher]
            
            result = build_data(self.filters)
            self.assertEqual(result, [])

    def test_edge_cases_payment_entry_dict(self):
        incomplete_entry = frappe._dict({
            'doctype': 'Payment Entry',
            'name': 'PE-00002'
        })
        
        result = build_payment_entry_dict(incomplete_entry)
        
        self.assertEqual(result['payment_document'], 'Payment Entry')
        self.assertEqual(result['payment_entry'], 'PE-00002')
        self.assertIsNone(result.get('posting_date'))
        self.assertIsNone(result.get('clearance_date'))

    def test_edge_cases_journal_entry_dict(self):
        incomplete_entry = frappe._dict({
            'doctype': 'Journal Entry',
            'name': 'JE-00002',
            'debit_in_account_currency': None,
            'credit_in_account_currency': None
        })
        
        result = build_journal_entry_dict(incomplete_entry)
        
        self.assertEqual(result['payment_document'], 'Journal Entry')
        self.assertEqual(result['payment_entry'], 'JE-00002')
        self.assertIsNone(result['debit'])
        self.assertIsNone(result['credit'])

    
    @patch('frappe.qb.from_')
    @patch('frappe.qb.DocType')
    def test_get_amounts_not_reflected_in_system_for_bank_reconciliation_statement(self, mock_doctype, mock_from):
        """Test get_amounts_not_reflected_in_system_for_bank_reconciliation_statement returns correct data"""
        
        # Mock data that should be returned by the queries
        mock_journal_entries = [
            frappe._dict({
                'doctype': 'Journal Entry',
                'name': 'JE-00001',
                'debit_in_account_currency': 1500.0,
                'credit_in_account_currency': 0.0,
                'posting_date': '2024-02-01',
                'clearance_date': '2024-01-30'
            })
        ]
        
        mock_payment_entries = [
            frappe._dict({
                'doctype': 'Payment Entry',
                'name': 'PE-00001',
                'amount': 2000.0,
                'payment_type': 'Receive',
                'party_type': 'Customer',
                'posting_date': '2024-02-01',
                'clearance_date': '2024-01-30'
            })
        ]
        
        # Setup query chain mocks
        mock_query = MagicMock()
        mock_query.inner_join.return_value = mock_query
        mock_query.on.return_value = mock_query
        mock_query.select.return_value = mock_query
        mock_query.where.return_value = mock_query
        
        # First call returns journal entries, second call returns payment entries
        mock_query.run.side_effect = [mock_journal_entries, mock_payment_entries]
        
        mock_from.return_value = mock_query
        mock_doctype.return_value = MagicMock()
        
        # Call the function
        result = get_amounts_not_reflected_in_system_for_bank_reconciliation_statement(self.filters)
        
        # Verify the result combines both journal and payment entries
        self.assertEqual(len(result), 2)
        
        # Check journal entry is included
        journal_entry = result[0]
        self.assertEqual(journal_entry['doctype'], 'Journal Entry')
        self.assertEqual(journal_entry['name'], 'JE-00001')
        self.assertEqual(journal_entry['debit_in_account_currency'], 1500.0)
        
        # Check payment entry is included
        payment_entry = result[1]
        self.assertEqual(payment_entry['doctype'], 'Payment Entry')
        self.assertEqual(payment_entry['name'], 'PE-00001')
        self.assertEqual(payment_entry['amount'], 2000.0)
        
        # Verify queries were executed
        self.assertEqual(mock_query.run.call_count, 2)
