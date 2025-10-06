#!/usr/bin/env python3
"""
Populate inventory with relevant printing/publishing industry items
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.models import InventoryItem
from database.managers import InventoryManager

def populate_inventory():
    """Populate the inventory with printing/publishing industry items"""

    inventory_items = [
        # PAPER PRODUCTS
        InventoryItem(
            sku="PP-A4-80GSM-001",
            name="A4 Copy Paper",
            description="Premium quality copy paper",
            price=450.00,
            tax_rate=18.0,
            default_discount_rate=5.0,
            category="Paper",
            unit="ream",
            stock_quantity=250,
            size_mm_length=297.0,
            size_mm_width=210.0,
            size_inches_length=11.7,
            size_inches_width=8.3,
            material="Paper",
            finish="Smooth",
            color="White",
            weight=2.5
        ),

        InventoryItem(
            sku="PP-A3-100GSM-002",
            name="A3 Poster Paper",
            description="High quality poster printing paper",
            price=850.00,
            tax_rate=18.0,
            default_discount_rate=7.0,
            category="Paper",
            unit="ream",
            stock_quantity=100,
            size_mm_length=420.0,
            size_mm_width=297.0,
            size_inches_length=16.5,
            size_inches_width=11.7,
            material="Paper",
            finish="Matte",
            color="White",
            weight=5.0
        ),

        InventoryItem(
            sku="PP-CARD-300GSM-003",
            name="Business Card Stock",
            description="Premium cardstock for business cards",
            price=1250.00,
            tax_rate=18.0,
            default_discount_rate=10.0,
            category="Cardstock",
            unit="sheet",
            stock_quantity=500,
            size_mm_length=90.0,
            size_mm_width=50.0,
            size_inches_length=3.5,
            size_inches_width=2.0,
            material="Cardstock",
            finish="Gloss",
            color="White",
            weight=0.3
        ),

        # PRINTING SUPPLIES
        InventoryItem(
            sku="INK-BLACK-HP-004",
            name="HP Black Ink Cartridge",
            description="Original HP black ink cartridge",
            price=2800.00,
            tax_rate=18.0,
            default_discount_rate=3.0,
            category="Ink",
            unit="piece",
            stock_quantity=75,
            material="Plastic",
            finish="Standard",
            color="Black",
            weight=0.2
        ),

        InventoryItem(
            sku="INK-COLOR-CANON-005",
            name="Canon Color Ink Set",
            description="Canon tri-color ink cartridge set",
            price=3500.00,
            tax_rate=18.0,
            default_discount_rate=5.0,
            category="Ink",
            unit="set",
            stock_quantity=40,
            material="Plastic",
            finish="Standard",
            color="Multi",
            weight=0.35
        ),

        # BINDING MATERIALS
        InventoryItem(
            sku="BIND-SPIRAL-A4-006",
            name="Spiral Binding Coils",
            description="Plastic spiral binding coils for A4",
            price=15.00,
            tax_rate=18.0,
            default_discount_rate=12.0,
            category="Binding",
            unit="piece",
            stock_quantity=1000,
            size_mm_length=297.0,
            size_mm_width=12.0,
            size_inches_length=11.7,
            size_inches_width=0.5,
            material="Plastic",
            finish="Standard",
            color="Black",
            weight=0.05
        ),

        InventoryItem(
            sku="BIND-COMB-A4-007",
            name="Comb Binding Rings",
            description="Plastic comb binding rings",
            price=25.00,
            tax_rate=18.0,
            default_discount_rate=15.0,
            category="Binding",
            unit="piece",
            stock_quantity=800,
            size_mm_length=297.0,
            size_mm_width=20.0,
            size_inches_length=11.7,
            size_inches_width=0.8,
            material="Plastic",
            finish="Standard",
            color="White",
            weight=0.08
        ),

        # LAMINATION SUPPLIES
        InventoryItem(
            sku="LAM-A4-GLOSS-008",
            name="A4 Lamination Film",
            description="Glossy lamination film for A4 documents",
            price=180.00,
            tax_rate=18.0,
            default_discount_rate=8.0,
            category="Lamination",
            unit="sheet",
            stock_quantity=500,
            size_mm_length=297.0,
            size_mm_width=210.0,
            size_inches_length=11.7,
            size_inches_width=8.3,
            material="Plastic",
            finish="Gloss",
            color="Clear",
            weight=0.05
        ),

        InventoryItem(
            sku="LAM-A3-MATTE-009",
            name="A3 Matte Lamination Film",
            description="Matte finish lamination film for A3",
            price=320.00,
            tax_rate=18.0,
            default_discount_rate=6.0,
            category="Lamination",
            unit="sheet",
            stock_quantity=300,
            size_mm_length=420.0,
            size_mm_width=297.0,
            size_inches_length=16.5,
            size_inches_width=11.7,
            material="Plastic",
            finish="Matte",
            color="Clear",
            weight=0.08
        ),

        # ENVELOPES
        InventoryItem(
            sku="ENV-DL-WHITE-010",
            name="DL Envelopes",
            description="Standard DL white envelopes",
            price=12.00,
            tax_rate=18.0,
            default_discount_rate=20.0,
            category="Envelopes",
            unit="piece",
            stock_quantity=2000,
            size_mm_length=220.0,
            size_mm_width=110.0,
            size_inches_length=8.7,
            size_inches_width=4.3,
            material="Paper",
            finish="Standard",
            color="White",
            weight=0.05
        ),

        InventoryItem(
            sku="ENV-A4-BROWN-011",
            name="A4 Brown Envelopes",
            description="Large brown kraft envelopes",
            price=35.00,
            tax_rate=18.0,
            default_discount_rate=15.0,
            category="Envelopes",
            unit="piece",
            stock_quantity=500,
            size_mm_length=324.0,
            size_mm_width=229.0,
            size_inches_length=12.8,
            size_inches_width=9.0,
            material="Kraft Paper",
            finish="Standard",
            color="Brown",
            weight=0.15
        ),

        # STATIONERY
        InventoryItem(
            sku="STAT-NOTE-A5-012",
            name="A5 Notebooks",
            description="Ruled A5 notebooks 200 pages",
            price=125.00,
            tax_rate=18.0,
            default_discount_rate=10.0,
            category="Stationery",
            unit="piece",
            stock_quantity=200,
            size_mm_length=210.0,
            size_mm_width=148.0,
            size_inches_length=8.3,
            size_inches_width=5.8,
            material="Paper",
            finish="Standard",
            color="White",
            weight=0.4
        ),

        InventoryItem(
            sku="STAT-PEN-BALL-013",
            name="Ballpoint Pens",
            description="Blue ink ballpoint pens",
            price=8.00,
            tax_rate=18.0,
            default_discount_rate=25.0,
            category="Stationery",
            unit="piece",
            stock_quantity=1500,
            size_mm_length=145.0,
            size_mm_width=8.0,
            size_inches_length=5.7,
            size_inches_width=0.3,
            material="Plastic",
            finish="Standard",
            color="Blue",
            weight=0.01
        ),

        # PACKAGING
        InventoryItem(
            sku="PACK-BOX-SMALL-014",
            name="Small Shipping Boxes",
            description="Corrugated shipping boxes",
            price=45.00,
            tax_rate=18.0,
            default_discount_rate=12.0,
            category="Packaging",
            unit="piece",
            stock_quantity=300,
            size_mm_length=200.0,
            size_mm_width=150.0,
            size_mm_height=100.0,
            size_inches_length=7.9,
            size_inches_width=5.9,
            size_inches_height=3.9,
            material="Cardboard",
            finish="Standard",
            color="Brown",
            weight=0.2
        ),

        InventoryItem(
            sku="PACK-TAPE-CLEAR-015",
            name="Packaging Tape",
            description="Clear packaging tape 48mm",
            price=65.00,
            tax_rate=18.0,
            default_discount_rate=8.0,
            category="Packaging",
            unit="roll",
            stock_quantity=150,
            size_mm_length=50000.0,
            size_mm_width=48.0,
            size_inches_length=1968.5,
            size_inches_width=1.9,
            material="Plastic",
            finish="Standard",
            color="Clear",
            weight=0.3
        )
    ]

    print("Populating inventory with printing/publishing industry items...")

    for item in inventory_items:
        try:
            item_id = InventoryManager.create_item(item)
            print(f"✅ Added: {item.name} (ID: {item_id}) - {item.get_display_text()}")
        except Exception as e:
            print(f"❌ Failed to add {item.name}: {str(e)}")

    print(f"\n🎉 Inventory population complete! Added {len(inventory_items)} items.")

if __name__ == "__main__":
    populate_inventory()