from datetime import datetime, date
from typing import List, Optional, Dict, Any
from src.database.database import db
from src.models.models import Customer, InventoryItem, Invoice, InvoiceItem, BusinessSettings

class CustomerManager:
    @staticmethod
    def create_customer(customer: Customer) -> int:
        """Create a new customer and return the ID"""
        query = """
            INSERT INTO customers (name, email, phone, address, gstin, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return db.execute_insert(query, (
            customer.name, customer.email, customer.phone,
            customer.address, customer.gstin, customer.notes
        ))

    @staticmethod
    def get_customer(customer_id: int) -> Optional[Customer]:
        """Get a customer by ID"""
        query = "SELECT * FROM customers WHERE id = ?"
        rows = db.execute_query(query, (customer_id,))
        if rows:
            row = rows[0]
            return Customer(**db.row_to_dict(row))
        return None

    @staticmethod
    def get_all_customers() -> List[Customer]:
        """Get all customers"""
        query = "SELECT * FROM customers ORDER BY name"
        rows = db.execute_query(query)
        return [Customer(**db.row_to_dict(row)) for row in rows]

    @staticmethod
    def search_customers(search_term: str) -> List[Customer]:
        """Search customers by name or email"""
        query = """
            SELECT * FROM customers
            WHERE name LIKE ? OR email LIKE ?
            ORDER BY name
        """
        term = f"%{search_term}%"
        rows = db.execute_query(query, (term, term))
        return [Customer(**db.row_to_dict(row)) for row in rows]

    @staticmethod
    def update_customer(customer: Customer) -> bool:
        """Update an existing customer"""
        query = """
            UPDATE customers
            SET name=?, email=?, phone=?, address=?, gstin=?, notes=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """
        affected = db.execute_update(query, (
            customer.name, customer.email, customer.phone,
            customer.address, customer.gstin, customer.notes, customer.id
        ))
        return affected > 0

    @staticmethod
    def delete_customer(customer_id: int) -> bool:
        """Delete a customer"""
        query = "DELETE FROM customers WHERE id = ?"
        affected = db.execute_update(query, (customer_id,))
        return affected > 0

class InventoryManager:
    @staticmethod
    def create_item(item: InventoryItem) -> int:
        """Create a new inventory item and return the ID"""
        query = """
            INSERT INTO inventory_items
            (sku, name, description, price, tax_rate, category, unit, stock_quantity, low_stock_alert, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return db.execute_insert(query, (
            item.sku, item.name, item.description, item.price, item.tax_rate,
            item.category, item.unit, item.stock_quantity, item.low_stock_alert, item.is_active
        ))

    @staticmethod
    def get_item(item_id: int) -> Optional[InventoryItem]:
        """Get an inventory item by ID"""
        query = "SELECT * FROM inventory_items WHERE id = ?"
        rows = db.execute_query(query, (item_id,))
        if rows:
            row = rows[0]
            return InventoryItem(**db.row_to_dict(row))
        return None

    @staticmethod
    def get_item_by_sku(sku: str) -> Optional[InventoryItem]:
        """Get an inventory item by SKU"""
        query = "SELECT * FROM inventory_items WHERE sku = ?"
        rows = db.execute_query(query, (sku,))
        if rows:
            row = rows[0]
            return InventoryItem(**db.row_to_dict(row))
        return None

    @staticmethod
    def get_all_items(active_only: bool = True) -> List[InventoryItem]:
        """Get all inventory items"""
        if active_only:
            query = "SELECT * FROM inventory_items WHERE is_active = 1 ORDER BY name"
        else:
            query = "SELECT * FROM inventory_items ORDER BY name"
        rows = db.execute_query(query)
        return [InventoryItem(**db.row_to_dict(row)) for row in rows]

    @staticmethod
    def search_items(search_term: str, active_only: bool = True) -> List[InventoryItem]:
        """Search inventory items by name, SKU, or description"""
        base_query = """
            SELECT * FROM inventory_items
            WHERE (name LIKE ? OR sku LIKE ? OR description LIKE ?)
        """
        if active_only:
            base_query += " AND is_active = 1"
        base_query += " ORDER BY name"

        term = f"%{search_term}%"
        rows = db.execute_query(base_query, (term, term, term))
        return [InventoryItem(**db.row_to_dict(row)) for row in rows]

    @staticmethod
    def update_item(item: InventoryItem) -> bool:
        """Update an existing inventory item"""
        query = """
            UPDATE inventory_items
            SET sku=?, name=?, description=?, price=?, tax_rate=?, category=?,
                unit=?, stock_quantity=?, low_stock_alert=?, is_active=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """
        affected = db.execute_update(query, (
            item.sku, item.name, item.description, item.price, item.tax_rate,
            item.category, item.unit, item.stock_quantity, item.low_stock_alert,
            item.is_active, item.id
        ))
        return affected > 0

    @staticmethod
    def delete_item(item_id: int) -> bool:
        """Delete an inventory item"""
        query = "DELETE FROM inventory_items WHERE id = ?"
        affected = db.execute_update(query, (item_id,))
        return affected > 0

    @staticmethod
    def get_low_stock_items() -> List[InventoryItem]:
        """Get items with low stock"""
        query = """
            SELECT * FROM inventory_items
            WHERE is_active = 1 AND stock_quantity <= low_stock_alert
            ORDER BY stock_quantity
        """
        rows = db.execute_query(query)
        return [InventoryItem(**db.row_to_dict(row)) for row in rows]

class InvoiceManager:
    @staticmethod
    def create_invoice(invoice: Invoice) -> str:
        """Create a new invoice and return the invoice_id"""
        # Insert invoice
        query = """
            INSERT INTO invoices
            (invoice_id, invoice_number, customer_id, customer_name, customer_email,
             customer_address, customer_gstin, date, due_date, notes, terms,
             subtotal, global_discount_rate, global_discount_amount, total_tax, grand_total, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        db.execute_insert(query, (
            invoice.invoice_id, invoice.invoice_number, invoice.customer_id,
            invoice.customer_name, invoice.customer_email, invoice.customer_address,
            invoice.customer_gstin, invoice.date, invoice.due_date, invoice.notes,
            invoice.terms, invoice.subtotal, invoice.global_discount_rate,
            invoice.global_discount_amount, invoice.total_tax, invoice.grand_total, invoice.status
        ))

        # Insert invoice items
        if invoice.items:
            item_query = """
                INSERT INTO invoice_items
                (invoice_id, item_id, sku, name, description, quantity, unit_price, discount_rate, tax_rate, line_total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            for item in invoice.items:
                db.execute_insert(item_query, (
                    invoice.invoice_id, item.item_id, item.sku, item.name,
                    item.description, item.quantity, item.unit_price,
                    item.discount_rate, item.tax_rate, item.line_total
                ))

        return invoice.invoice_id

    @staticmethod
    def get_invoice(invoice_id: str) -> Optional[Invoice]:
        """Get an invoice with its items"""
        # Get invoice
        query = "SELECT * FROM invoices WHERE invoice_id = ?"
        rows = db.execute_query(query, (invoice_id,))
        if not rows:
            return None

        invoice_data = db.row_to_dict(rows[0])
        invoice = Invoice(**invoice_data)

        # Get invoice items
        items_query = "SELECT * FROM invoice_items WHERE invoice_id = ? ORDER BY id"
        item_rows = db.execute_query(items_query, (invoice_id,))
        invoice.items = [InvoiceItem(**db.row_to_dict(row)) for row in item_rows]

        return invoice

    @staticmethod
    def get_all_invoices(limit: int = 100) -> List[Invoice]:
        """Get all invoices (without items for performance)"""
        query = "SELECT * FROM invoices ORDER BY date DESC, created_at DESC LIMIT ?"
        rows = db.execute_query(query, (limit,))
        return [Invoice(**db.row_to_dict(row)) for row in rows]

    @staticmethod
    def search_invoices(search_term: str = "", status: str = "", limit: int = 100) -> List[Invoice]:
        """Search invoices"""
        conditions = []
        params = []

        if search_term:
            conditions.append("(invoice_number LIKE ? OR customer_name LIKE ?)")
            term = f"%{search_term}%"
            params.extend([term, term])

        if status:
            conditions.append("status = ?")
            params.append(status)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT * FROM invoices {where_clause} ORDER BY date DESC, created_at DESC LIMIT ?"
        params.append(limit)

        rows = db.execute_query(query, tuple(params))
        return [Invoice(**db.row_to_dict(row)) for row in rows]

    @staticmethod
    def update_invoice(invoice: Invoice) -> bool:
        """Update an existing invoice"""
        # Update invoice
        query = """
            UPDATE invoices
            SET customer_id=?, customer_name=?, customer_email=?, customer_address=?, customer_gstin=?,
                date=?, due_date=?, notes=?, terms=?, subtotal=?, global_discount_rate=?,
                global_discount_amount=?, total_tax=?, grand_total=?, status=?, updated_at=CURRENT_TIMESTAMP
            WHERE invoice_id=?
        """
        affected = db.execute_update(query, (
            invoice.customer_id, invoice.customer_name, invoice.customer_email,
            invoice.customer_address, invoice.customer_gstin, invoice.date,
            invoice.due_date, invoice.notes, invoice.terms, invoice.subtotal,
            invoice.global_discount_rate, invoice.global_discount_amount,
            invoice.total_tax, invoice.grand_total, invoice.status, invoice.invoice_id
        ))

        # Delete existing items and re-insert
        db.execute_update("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice.invoice_id,))

        if invoice.items:
            item_query = """
                INSERT INTO invoice_items
                (invoice_id, item_id, sku, name, description, quantity, unit_price, discount_rate, tax_rate, line_total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            for item in invoice.items:
                db.execute_insert(item_query, (
                    invoice.invoice_id, item.item_id, item.sku, item.name,
                    item.description, item.quantity, item.unit_price,
                    item.discount_rate, item.tax_rate, item.line_total
                ))

        return affected > 0

    @staticmethod
    def delete_invoice(invoice_id: str) -> bool:
        """Delete an invoice and its items"""
        # Delete items first (foreign key constraint)
        db.execute_update("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))

        # Delete invoice
        affected = db.execute_update("DELETE FROM invoices WHERE invoice_id = ?", (invoice_id,))
        return affected > 0

    @staticmethod
    def get_next_invoice_number() -> str:
        """Get the next invoice number"""
        settings = SettingsManager.get_settings()
        current_number = settings.invoice_counter
        prefix = settings.invoice_prefix

        # Update counter
        SettingsManager.update_invoice_counter(current_number + 1)

        return f"{prefix}-{current_number:04d}"

class SettingsManager:
    @staticmethod
    def get_settings() -> BusinessSettings:
        """Get business settings"""
        query = "SELECT * FROM business_settings ORDER BY id LIMIT 1"
        rows = db.execute_query(query)
        if rows:
            return BusinessSettings(**db.row_to_dict(rows[0]))
        return BusinessSettings()

    @staticmethod
    def update_settings(settings: BusinessSettings) -> bool:
        """Update business settings"""
        query = """
            UPDATE business_settings
            SET business_name=?, business_address=?, business_phone=?, business_email=?, business_gstin=?,
                business_logo_path=?, invoice_prefix=?, invoice_counter=?, currency_symbol=?, default_tax_rate=?,
                smtp_server=?, smtp_port=?, smtp_username=?, smtp_password=?,
                terms_and_conditions=?, notes_footer=?, updated_at=CURRENT_TIMESTAMP
            WHERE id = (SELECT id FROM business_settings ORDER BY id LIMIT 1)
        """
        affected = db.execute_update(query, (
            settings.business_name, settings.business_address, settings.business_phone,
            settings.business_email, settings.business_gstin, settings.business_logo_path,
            settings.invoice_prefix, settings.invoice_counter, settings.currency_symbol,
            settings.default_tax_rate, settings.smtp_server, settings.smtp_port,
            settings.smtp_username, settings.smtp_password, settings.terms_and_conditions,
            settings.notes_footer
        ))
        return affected > 0

    @staticmethod
    def update_invoice_counter(counter: int) -> bool:
        """Update just the invoice counter"""
        query = """
            UPDATE business_settings
            SET invoice_counter=?, updated_at=CURRENT_TIMESTAMP
            WHERE id = (SELECT id FROM business_settings ORDER BY id LIMIT 1)
        """
        affected = db.execute_update(query, (counter,))
        return affected > 0