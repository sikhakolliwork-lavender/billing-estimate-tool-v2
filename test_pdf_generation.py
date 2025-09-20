#!/usr/bin/env python3
"""
Test script to verify PDF generation with fixed styling
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.models import BusinessSettings, Invoice, InvoiceItem
from utils.pdf_generator import PDFInvoiceGenerator

def test_pdf_generation():
    """Test PDF generation with sample data"""

    # Create business settings
    business_settings = BusinessSettings(
        business_name="Test Company Ltd",
        business_address="123 Test Street\nTest City, TC 12345",
        business_phone="+1-555-123-4567",
        business_email="test@testcompany.com",
        business_gstin="22AAAAA0000A1Z5",
        currency_symbol="$",
        terms_and_conditions="Payment due within 30 days.",
        notes_footer="Thank you for your business!"
    )

    # Create sample invoice items
    items = [
        InvoiceItem(
            name="Test Product 1",
            quantity=2.0,
            unit_price=100.00,
            discount_rate=10.0,
            line_total=180.00
        ),
        InvoiceItem(
            name="Test Service 1",
            quantity=1.0,
            unit_price=250.00,
            discount_rate=0.0,
            line_total=250.00
        )
    ]

    # Create invoice
    invoice = Invoice(
        invoice_number="TEST-001",
        customer_name="Test Customer",
        customer_address="456 Customer St\nCustomer City, CC 67890",
        customer_email="customer@test.com",
        customer_gstin="33BBBBB0000B1Z5",
        date=datetime.now().strftime("%Y-%m-%d"),
        due_date="2024-10-20",
        items=items,
        subtotal=430.00,
        global_discount_rate=5.0,
        global_discount_amount=21.50,
        total_tax=73.53,
        grand_total=482.03,
        notes="This is a test invoice.",
        terms="Payment due within 30 days.",
        status="draft"
    )

    # Generate PDF
    try:
        pdf_generator = PDFInvoiceGenerator(business_settings)
        pdf_path = pdf_generator.generate_invoice_pdf(invoice)

        print(f"✅ PDF generated successfully: {pdf_path}")

        # Verify file exists and has content
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"✅ PDF file size: {file_size} bytes")

            if file_size > 1000:  # Should be at least 1KB for a real PDF
                print("✅ PDF generation test PASSED!")
                return True
            else:
                print("❌ PDF file seems too small")
                return False
        else:
            print("❌ PDF file was not created")
            return False

    except Exception as e:
        print(f"❌ PDF generation failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing PDF generation with fixed styling...")
    success = test_pdf_generation()

    if success:
        print("\n🎉 All tests passed! PDF generation is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Tests failed! There are still issues with PDF generation.")
        sys.exit(1)