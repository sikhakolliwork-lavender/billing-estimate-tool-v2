from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import uuid

@dataclass
class Customer:
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    gstin: str = ""
    notes: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class InventoryItem:
    id: Optional[int] = None
    sku: str = ""
    name: str = ""
    description: str = ""
    price: float = 0.0
    tax_rate: float = 18.0  # Default GST rate
    category: str = ""
    unit: str = "nos"  # pieces, kg, meters, etc.
    stock_quantity: int = 0
    low_stock_alert: int = 10
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class InvoiceItem:
    id: Optional[int] = None
    invoice_id: str = ""
    item_id: Optional[int] = None
    sku: str = ""
    name: str = ""
    description: str = ""
    quantity: float = 1.0
    unit_price: float = 0.0
    discount_rate: float = 0.0
    tax_rate: float = 18.0
    line_total: float = 0.0

@dataclass
class Invoice:
    id: Optional[int] = None
    invoice_id: str = ""
    invoice_number: str = ""
    customer_id: Optional[int] = None
    customer_name: str = ""
    customer_email: str = ""
    customer_address: str = ""
    customer_gstin: str = ""

    # Invoice details
    date: str = ""
    due_date: str = ""
    notes: str = ""
    terms: str = ""

    # Amounts
    subtotal: float = 0.0
    global_discount_rate: float = 0.0
    global_discount_amount: float = 0.0
    total_tax: float = 0.0
    grand_total: float = 0.0

    # Status and metadata
    status: str = "draft"  # draft, sent, paid, cancelled
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Items (not stored in DB, loaded separately)
    items: List[InvoiceItem] = None

    def __post_init__(self):
        if self.items is None:
            self.items = []
        if not self.invoice_id:
            self.invoice_id = str(uuid.uuid4())

@dataclass
class BusinessSettings:
    id: Optional[int] = None
    business_name: str = "Your Business"
    business_address: str = ""
    business_phone: str = ""
    business_email: str = ""
    business_gstin: str = ""
    business_logo_path: str = ""

    # Invoice settings
    invoice_prefix: str = "INV"
    invoice_counter: int = 1
    currency_symbol: str = "₹"
    default_tax_rate: float = 18.0

    # Email settings
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""

    # Other settings
    terms_and_conditions: str = ""
    notes_footer: str = ""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None