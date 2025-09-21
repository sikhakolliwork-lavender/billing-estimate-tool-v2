#!/usr/bin/env python3
"""
Test script to generate PDF with 10 items to test layout with more items
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.models import BusinessSettings, Estimate, EstimateItem
from utils.pdf_generator import PDFEstimateGenerator

def test_large_pdf_generation():
    """Test PDF generation with 10 items"""

    # Create business settings
    business_settings = BusinessSettings(
        business_name="Tech Solutions India Pvt Ltd",
        business_address="123 Business Park\nBangalore, Karnataka 560001\nIndia",
        business_phone="+91-80-1234-5678",
        business_email="info@techsolutions.in",
        business_gstin="29AAAAA0000A1Z5",
        currency_symbol="₹",
        terms_and_conditions="Payment due within 30 days. Late payments may incur additional charges.",
        notes_footer="Thank you for choosing Tech Solutions India. We appreciate your business!"
    )

    # Create 10 sample estimate items with varied descriptions
    items = [
        EstimateItem(
            name="4K Monitor - 27-inch 4K UHD monitor with HDR support",
            quantity=2.0,
            unit_price=35000.00,
            discount_rate=5.0,
            line_total=66500.00
        ),
        EstimateItem(
            name="Wireless Gaming Mouse - RGB lighting, 16000 DPI, ergonomic design",
            quantity=5.0,
            unit_price=2500.00,
            discount_rate=10.0,
            line_total=11250.00
        ),
        EstimateItem(
            name="Mechanical Keyboard - Cherry MX switches, backlit keys, compact design",
            quantity=3.0,
            unit_price=8500.00,
            discount_rate=0.0,
            line_total=25500.00
        ),
        EstimateItem(
            name="Laptop Stand - Adjustable aluminum stand with cooling fans",
            quantity=4.0,
            unit_price=1200.00,
            discount_rate=15.0,
            line_total=4080.00
        ),
        EstimateItem(
            name="USB-C Hub - 7-in-1 hub with HDMI, USB 3.0, SD card reader",
            quantity=6.0,
            unit_price=3200.00,
            discount_rate=8.0,
            line_total=17664.00
        ),
        EstimateItem(
            name="Webcam HD - 1080p webcam with auto-focus and noise cancellation",
            quantity=8.0,
            unit_price=4500.00,
            discount_rate=12.0,
            line_total=31680.00
        ),
        EstimateItem(
            name="External SSD - 1TB portable SSD with USB-C, high-speed data transfer",
            quantity=3.0,
            unit_price=12000.00,
            discount_rate=5.0,
            line_total=34200.00
        ),
        EstimateItem(
            name="Bluetooth Headphones - Noise cancelling, 30-hour battery, premium sound",
            quantity=4.0,
            unit_price=15000.00,
            discount_rate=20.0,
            line_total=48000.00
        ),
        EstimateItem(
            name="Desk Organizer - Wooden desk organizer with multiple compartments",
            quantity=2.0,
            unit_price=800.00,
            discount_rate=0.0,
            line_total=1600.00
        ),
        EstimateItem(
            name="Cable Management Kit - Cable clips, sleeves, and ties for clean setup",
            quantity=10.0,
            unit_price=150.00,
            discount_rate=25.0,
            line_total=1125.00
        )
    ]

    # Calculate totals
    subtotal = sum(item.line_total for item in items)
    global_discount_rate = 2.0
    global_discount_amount = subtotal * (global_discount_rate / 100)
    after_discount = subtotal - global_discount_amount
    tax_rate = 18.0  # GST
    total_tax = after_discount * (tax_rate / 100)
    grand_total = after_discount + total_tax

    # Create estimate
    estimate = Estimate(
        estimate_number="EST-2024-010",
        customer_name="ABC Technologies Pvt Ltd",
        customer_address="456 Tech Park\nHyderabad, Telangana 500081\nIndia",
        customer_email="procurement@abctech.com",
        customer_gstin="36BBBBB0000B1Z5",
        date=datetime.now().strftime("%Y-%m-%d"),
        due_date="2024-11-15",
        items=items,
        subtotal=subtotal,
        global_discount_rate=global_discount_rate,
        global_discount_amount=global_discount_amount,
        total_tax=total_tax,
        grand_total=grand_total,
        notes="This estimate includes bulk discount pricing. All items come with 1-year warranty.",
        terms="Payment terms: 30 days net. Delivery within 7-10 business days after order confirmation.",
        status="draft"
    )

    # Generate PDF
    try:
        pdf_generator = PDFEstimateGenerator(business_settings)
        pdf_path = pdf_generator.generate_estimate_pdf(estimate)

        print(f"✅ PDF with 10 items generated successfully: {pdf_path}")
        print(f"📊 Estimate Summary:")
        print(f"   - Number of items: {len(items)}")
        print(f"   - Subtotal: ₹{subtotal:,.2f}")
        print(f"   - Global discount ({global_discount_rate}%): ₹{global_discount_amount:,.2f}")
        print(f"   - Tax (GST {tax_rate}%): ₹{total_tax:,.2f}")
        print(f"   - Grand total: ₹{grand_total:,.2f}")

        # Verify file exists and has content
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"✅ PDF file size: {file_size} bytes")

            if file_size > 2000:  # Should be larger for 10 items
                print("✅ Large PDF generation test PASSED!")
                print(f"🔍 Opening PDF: {pdf_path}")
                # Open the PDF
                os.system(f"open '{pdf_path}'")
                return True
            else:
                print("❌ PDF file seems too small for 10 items")
                return False
        else:
            print("❌ PDF file was not created")
            return False

    except Exception as e:
        print(f"❌ PDF generation failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing PDF generation with 10 items...")
    success = test_large_pdf_generation()

    if success:
        print("\n🎉 Large PDF test passed! Check the opened PDF for formatting.")
    else:
        print("\n💥 Large PDF test failed!")