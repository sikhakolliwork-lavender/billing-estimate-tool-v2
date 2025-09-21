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
    default_discount_rate: float = 0.0  # Default discount percentage
    category: str = ""
    unit: str = "nos"  # pieces, kg, meters, etc.
    stock_quantity: int = 0
    low_stock_alert: int = 10

    # Size information - both metric and imperial
    size_mm_length: Optional[float] = None
    size_mm_width: Optional[float] = None
    size_mm_height: Optional[float] = None
    size_inches_length: Optional[float] = None
    size_inches_width: Optional[float] = None
    size_inches_height: Optional[float] = None

    # Additional specifications
    material: str = ""
    finish: str = ""
    color: str = ""
    weight: Optional[float] = None

    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def get_display_text(self) -> str:
        """Generate combined display text with all item details separated by |"""
        parts = [self.name]

        if self.description:
            parts.append(self.description)

        # Add size information if available
        if self.size_mm_length and self.size_mm_width:
            if self.size_mm_height:
                size_mm = f"{self.size_mm_length}x{self.size_mm_width}x{self.size_mm_height}mm"
            else:
                size_mm = f"{self.size_mm_length}x{self.size_mm_width}mm"
            parts.append(size_mm)

        if self.size_inches_length and self.size_inches_width:
            if self.size_inches_height:
                size_inches = f"{self.size_inches_length}\"x{self.size_inches_width}\"x{self.size_inches_height}\""
            else:
                size_inches = f"{self.size_inches_length}\"x{self.size_inches_width}\""
            parts.append(size_inches)

        # Add material and finish
        if self.material:
            parts.append(self.material)
        if self.finish:
            parts.append(self.finish)
        if self.color:
            parts.append(self.color)

        # Add weight if specified
        if self.weight:
            parts.append(f"{self.weight}kg")

        # Add SKU
        if self.sku:
            parts.append(f"SKU: {self.sku}")

        return " | ".join(parts)

@dataclass
class EstimateItem:
    id: Optional[int] = None
    estimate_id: str = ""
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
class Estimate:
    id: Optional[int] = None
    estimate_id: str = ""
    estimate_number: str = ""
    customer_id: Optional[int] = None
    customer_name: str = ""
    customer_email: str = ""
    customer_address: str = ""
    customer_gstin: str = ""

    # Estimate details
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
    status: str = "draft"  # draft, sent, accepted, cancelled
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Items (not stored in DB, loaded separately)
    items: List[EstimateItem] = None

    def __post_init__(self):
        if self.items is None:
            self.items = []
        if not self.estimate_id:
            self.estimate_id = str(uuid.uuid4())

@dataclass
class BusinessSettings:
    id: Optional[int] = None
    business_name: str = "Your Business"
    business_address: str = ""
    business_phone: str = ""
    business_email: str = ""
    business_gstin: str = ""
    business_logo_path: str = ""

    # Estimate settings
    estimate_prefix: str = "INV"
    estimate_counter: int = 1
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