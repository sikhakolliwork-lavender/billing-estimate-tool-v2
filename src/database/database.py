import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str = "data/database.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()

    def init_database(self):
        """Initialize database with all required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    gstin TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Inventory items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sku TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL DEFAULT 0.0,
                    tax_rate REAL NOT NULL DEFAULT 18.0,
                    category TEXT,
                    unit TEXT DEFAULT 'nos',
                    stock_quantity INTEGER DEFAULT 0,
                    low_stock_alert INTEGER DEFAULT 10,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Invoices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id TEXT UNIQUE NOT NULL,
                    invoice_number TEXT UNIQUE NOT NULL,
                    customer_id INTEGER,
                    customer_name TEXT NOT NULL,
                    customer_email TEXT,
                    customer_address TEXT,
                    customer_gstin TEXT,

                    date TEXT NOT NULL,
                    due_date TEXT,
                    notes TEXT,
                    terms TEXT,

                    subtotal REAL NOT NULL DEFAULT 0.0,
                    global_discount_rate REAL DEFAULT 0.0,
                    global_discount_amount REAL DEFAULT 0.0,
                    total_tax REAL DEFAULT 0.0,
                    grand_total REAL NOT NULL DEFAULT 0.0,

                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            """)

            # Invoice items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoice_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id TEXT NOT NULL,
                    item_id INTEGER,
                    sku TEXT,
                    name TEXT NOT NULL,
                    description TEXT,
                    quantity REAL NOT NULL DEFAULT 1.0,
                    unit_price REAL NOT NULL DEFAULT 0.0,
                    discount_rate REAL DEFAULT 0.0,
                    tax_rate REAL DEFAULT 18.0,
                    line_total REAL NOT NULL DEFAULT 0.0,

                    FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id),
                    FOREIGN KEY (item_id) REFERENCES inventory_items (id)
                )
            """)

            # Business settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS business_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_name TEXT DEFAULT 'Your Business',
                    business_address TEXT,
                    business_phone TEXT,
                    business_email TEXT,
                    business_gstin TEXT,
                    business_logo_path TEXT,

                    invoice_prefix TEXT DEFAULT 'INV',
                    invoice_counter INTEGER DEFAULT 1,
                    currency_symbol TEXT DEFAULT '₹',
                    default_tax_rate REAL DEFAULT 18.0,

                    smtp_server TEXT,
                    smtp_port INTEGER DEFAULT 587,
                    smtp_username TEXT,
                    smtp_password TEXT,

                    terms_and_conditions TEXT,
                    notes_footer TEXT,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_name ON customers (name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_sku ON inventory_items (sku)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_name ON inventory_items (name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_number ON invoices (invoice_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices (date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices (status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice_id ON invoice_items (invoice_id)")

            # Insert default business settings if not exists
            cursor.execute("SELECT COUNT(*) FROM business_settings")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO business_settings (
                        business_name, currency_symbol, default_tax_rate,
                        terms_and_conditions, notes_footer
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    "Your Business Name",
                    "₹",
                    18.0,
                    "Payment is due within 30 days from the date of invoice.",
                    "Thank you for your business!"
                ))

            conn.commit()

    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the new row ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a sqlite3.Row to a dictionary"""
        return dict(row) if row else {}

    def backup_database(self, backup_path: str = None) -> str:
        """Create a backup of the database"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/backups/backup_{timestamp}.db"

        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        with self.get_connection() as source:
            with sqlite3.connect(backup_path) as backup:
                source.backup(backup)

        return str(backup_path)

# Global database instance
db = DatabaseManager()