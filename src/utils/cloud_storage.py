"""
Cloud Storage Utilities for Streamlit Deployment

This module provides data persistence and file handling solutions
for cloud deployment where local file storage is not persistent.
"""

import streamlit as st
import json
import io
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.models.models import Customer, InventoryItem, Estimate, BusinessSettings


class CloudDataManager:
    """Manages data persistence using Streamlit session state for cloud deployment"""

    def __init__(self):
        self._init_session_state()

    def _init_session_state(self):
        """Initialize session state with default data"""
        if 'customers' not in st.session_state:
            st.session_state.customers = []

        if 'inventory_items' not in st.session_state:
            st.session_state.inventory_items = self._get_default_inventory()

        if 'estimates' not in st.session_state:
            st.session_state.estimates = []

        if 'business_settings' not in st.session_state:
            st.session_state.business_settings = self._get_default_business_settings()

        if 'estimate_counter' not in st.session_state:
            st.session_state.estimate_counter = 1

    def _get_default_business_settings(self) -> Dict[str, Any]:
        """Get default business settings"""
        return {
            'business_name': 'Your Business Name',
            'business_address': '123 Business Street\nYour City, State 12345',
            'business_phone': '+1-555-123-4567',
            'business_email': 'info@yourbusiness.com',
            'business_gstin': 'GSTIN123456789',
            'currency_symbol': '₹',
            'estimate_prefix': 'EST',
            'estimate_counter': 1,
            'default_tax_rate': 18.0,
            'terms_and_conditions': 'Payment due within 30 days.',
            'notes_footer': 'Thank you for your business!'
        }

    def _get_default_inventory(self) -> List[Dict[str, Any]]:
        """Get default inventory items"""
        return [
            {
                'id': 1,
                'sku': 'MONITOR001',
                'name': '4K Monitor',
                'description': '27-inch 4K UHD monitor with HDR support',
                'price': 35000.00,
                'tax_rate': 18.0,
                'default_discount_rate': 5.0,
                'category': 'Electronics',
                'unit': 'piece',
                'stock_quantity': 10,
                'low_stock_alert': 2,
                'is_active': True
            },
            {
                'id': 2,
                'sku': 'MOUSE001',
                'name': 'Wireless Gaming Mouse',
                'description': 'RGB lighting, 16000 DPI, ergonomic design',
                'price': 2500.00,
                'tax_rate': 18.0,
                'default_discount_rate': 10.0,
                'category': 'Electronics',
                'unit': 'piece',
                'stock_quantity': 25,
                'low_stock_alert': 5,
                'is_active': True
            },
            {
                'id': 3,
                'sku': 'KEYBOARD001',
                'name': 'Mechanical Keyboard',
                'description': 'Cherry MX switches, backlit keys, compact design',
                'price': 8500.00,
                'tax_rate': 18.0,
                'default_discount_rate': 0.0,
                'category': 'Electronics',
                'unit': 'piece',
                'stock_quantity': 15,
                'low_stock_alert': 3,
                'is_active': True
            }
        ]

    # Customer methods
    def get_customers(self) -> List[Dict[str, Any]]:
        """Get all customers"""
        return st.session_state.customers

    def add_customer(self, customer_data: Dict[str, Any]) -> int:
        """Add a new customer"""
        customer_id = len(st.session_state.customers) + 1
        customer_data['id'] = customer_id
        customer_data['created_at'] = datetime.now().isoformat()
        st.session_state.customers.append(customer_data)
        return customer_id

    def update_customer(self, customer_id: int, customer_data: Dict[str, Any]) -> bool:
        """Update an existing customer"""
        for i, customer in enumerate(st.session_state.customers):
            if customer['id'] == customer_id:
                customer_data['id'] = customer_id
                customer_data['updated_at'] = datetime.now().isoformat()
                st.session_state.customers[i] = customer_data
                return True
        return False

    def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer"""
        st.session_state.customers = [c for c in st.session_state.customers if c['id'] != customer_id]
        return True

    # Inventory methods
    def get_inventory_items(self) -> List[Dict[str, Any]]:
        """Get all inventory items"""
        return st.session_state.inventory_items

    def add_inventory_item(self, item_data: Dict[str, Any]) -> int:
        """Add a new inventory item"""
        item_id = max([item['id'] for item in st.session_state.inventory_items], default=0) + 1
        item_data['id'] = item_id
        item_data['created_at'] = datetime.now().isoformat()
        st.session_state.inventory_items.append(item_data)
        return item_id

    def update_inventory_item(self, item_id: int, item_data: Dict[str, Any]) -> bool:
        """Update an existing inventory item"""
        for i, item in enumerate(st.session_state.inventory_items):
            if item['id'] == item_id:
                item_data['id'] = item_id
                item_data['updated_at'] = datetime.now().isoformat()
                st.session_state.inventory_items[i] = item_data
                return True
        return False

    def search_inventory_items(self, search_term: str) -> List[Dict[str, Any]]:
        """Search inventory items by name or SKU"""
        search_term = search_term.lower()
        return [
            item for item in st.session_state.inventory_items
            if search_term in item['name'].lower() or search_term in item['sku'].lower()
        ]

    # Estimate methods
    def get_estimates(self) -> List[Dict[str, Any]]:
        """Get all estimates"""
        return st.session_state.estimates

    def add_estimate(self, estimate_data: Dict[str, Any]) -> str:
        """Add a new estimate"""
        estimate_id = f"EST-{st.session_state.estimate_counter:04d}"
        estimate_data['estimate_id'] = estimate_id
        estimate_data['estimate_number'] = estimate_id
        estimate_data['created_at'] = datetime.now().isoformat()
        st.session_state.estimates.append(estimate_data)
        st.session_state.estimate_counter += 1
        return estimate_id

    def get_estimate(self, estimate_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific estimate"""
        for estimate in st.session_state.estimates:
            if estimate.get('estimate_id') == estimate_id:
                return estimate
        return None

    def update_estimate(self, estimate_id: str, estimate_data: Dict[str, Any]) -> bool:
        """Update an existing estimate"""
        for i, estimate in enumerate(st.session_state.estimates):
            if estimate.get('estimate_id') == estimate_id:
                estimate_data['estimate_id'] = estimate_id
                estimate_data['updated_at'] = datetime.now().isoformat()
                st.session_state.estimates[i] = estimate_data
                return True
        return False

    # Business settings methods
    def get_business_settings(self) -> Dict[str, Any]:
        """Get business settings"""
        return st.session_state.business_settings

    def update_business_settings(self, settings: Dict[str, Any]) -> bool:
        """Update business settings"""
        st.session_state.business_settings.update(settings)
        return True

    def get_next_estimate_number(self) -> str:
        """Get the next estimate number"""
        settings = self.get_business_settings()
        current_number = st.session_state.estimate_counter
        prefix = settings.get('estimate_prefix', 'EST')
        st.session_state.estimate_counter += 1
        return f"{prefix}-{current_number:04d}"


class CloudFileManager:
    """Manages file operations for cloud deployment"""

    @staticmethod
    def create_pdf_download_link(pdf_bytes: bytes, filename: str) -> None:
        """Create a download link for PDF file"""
        st.download_button(
            label="📄 Download PDF",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            help="Click to download the generated PDF estimate"
        )

    @staticmethod
    def export_data_as_json() -> str:
        """Export all session data as JSON"""
        export_data = {
            'customers': st.session_state.get('customers', []),
            'inventory_items': st.session_state.get('inventory_items', []),
            'estimates': st.session_state.get('estimates', []),
            'business_settings': st.session_state.get('business_settings', {}),
            'export_timestamp': datetime.now().isoformat()
        }
        return json.dumps(export_data, indent=2)

    @staticmethod
    def import_data_from_json(json_data: str) -> bool:
        """Import data from JSON string"""
        try:
            data = json.loads(json_data)

            if 'customers' in data:
                st.session_state.customers = data['customers']
            if 'inventory_items' in data:
                st.session_state.inventory_items = data['inventory_items']
            if 'estimates' in data:
                st.session_state.estimates = data['estimates']
            if 'business_settings' in data:
                st.session_state.business_settings = data['business_settings']

            st.success("✅ Data imported successfully!")
            return True
        except Exception as e:
            st.error(f"❌ Error importing data: {str(e)}")
            return False


# Global instance for easy access
cloud_data_manager = CloudDataManager()
cloud_file_manager = CloudFileManager()