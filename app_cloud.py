"""
Cloud-Ready Billing & Estimate Manager

This is the cloud deployment version that uses session state for data persistence
and provides PDF downloads instead of file storage.
"""

import streamlit as st
import os
from datetime import datetime
from typing import Optional, Dict, Any

# Set up imports based on deployment environment
try:
    from src.utils.cloud_storage import cloud_data_manager, cloud_file_manager
    from src.utils.cloud_pdf_generator import CloudPDFEstimateGenerator
    from src.models.models import BusinessSettings, Estimate, EstimateItem
    import tally_bridge
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()


def initialize_app():
    """Initialize the Streamlit app with proper configuration"""
    st.set_page_config(
        page_title="Billing & Estimate Manager",
        page_icon="🧾",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def create_estimate_page():
    """Create estimate page with cloud-compatible features"""
    st.title("🧾 Create New Estimate")

    # Get business settings from cloud storage
    business_settings_dict = cloud_data_manager.get_business_settings()
    business_settings = BusinessSettings(**business_settings_dict)

    # Customer selection
    col1, col2 = st.columns([2, 1])

    with col1:
        customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
        customer_address = st.text_area("Customer Address", placeholder="Enter customer address")

    with col2:
        customer_email = st.text_input("Customer Email", placeholder="customer@email.com")
        customer_gstin = st.text_input("Customer GSTIN", placeholder="GST Number")

    # Estimate details
    col3, col4, col5 = st.columns(3)

    with col3:
        estimate_number = st.text_input("Estimate Number", value=cloud_data_manager.get_next_estimate_number())

    with col4:
        estimate_date = st.date_input("Estimate Date", value=datetime.now().date())

    with col5:
        due_date = st.date_input("Due Date")

    # Notes and terms
    col6, col7 = st.columns(2)

    with col6:
        notes = st.text_area("Notes", placeholder="Any additional notes...")

    with col7:
        terms = st.text_area("Terms & Conditions",
                           value=business_settings.terms_and_conditions,
                           placeholder="Payment terms...")

    # Get inventory items for the component
    inventory_items = cloud_data_manager.get_inventory_items()

    # Tally Bridge Component
    st.subheader("💼 Line Items")

    # Convert inventory to the format expected by tally_bridge
    inventory_for_component = [
        {
            "id": item["id"],
            "name": item["name"],
            "price": item["price"],
            "tax_rate": item.get("tax_rate", 18.0),
            "discount_rate": item.get("default_discount_rate", 0.0)
        }
        for item in inventory_items
    ]

    # Render the tally bridge component
    result = tally_bridge.tally_bridge(
        inventory=inventory_for_component,
        currency_symbol=business_settings.currency_symbol,
        key="estimate_creator"
    )

    # Save estimate button and PDF generation
    col8, col9, col10 = st.columns([1, 1, 1])

    with col9:
        if st.button("💾 Save & Generate PDF", type="primary", use_container_width=True):
            if result and result.get("lines"):
                # Validate required fields
                if not customer_name:
                    st.error("❌ Customer name is required!")
                    return

                # Process the result
                lines = result["lines"]
                global_discount = result.get("globalDiscount", 0)
                global_tax = result.get("globalTax", 18)

                # Create estimate items
                estimate_items = []
                subtotal = 0

                for line in lines:
                    if line.get("item") and line.get("quantity", 0) > 0:
                        # Calculate line totals
                        quantity = float(line["quantity"])
                        rate = float(line["rate"])
                        discount = float(line.get("discount", 0))

                        line_before_discount = quantity * rate
                        line_discount_amount = line_before_discount * (discount / 100)
                        line_total = line_before_discount - line_discount_amount

                        item = EstimateItem(
                            name=line["item"],
                            quantity=quantity,
                            unit_price=rate,
                            discount_rate=discount,
                            line_total=line_total,
                            tax_rate=global_tax
                        )
                        estimate_items.append(item)
                        subtotal += line_total

                if not estimate_items:
                    st.error("❌ Please add at least one item to the estimate!")
                    return

                # Calculate totals
                global_discount_amount = subtotal * (global_discount / 100)
                after_discount = subtotal - global_discount_amount
                tax_amount = after_discount * (global_tax / 100)
                grand_total = after_discount + tax_amount

                # Create estimate object
                estimate = Estimate(
                    estimate_number=estimate_number,
                    customer_name=customer_name,
                    customer_address=customer_address,
                    customer_email=customer_email,
                    customer_gstin=customer_gstin,
                    date=estimate_date.strftime("%Y-%m-%d"),
                    due_date=due_date.strftime("%Y-%m-%d") if due_date else None,
                    items=estimate_items,
                    subtotal=subtotal,
                    global_discount_rate=global_discount,
                    global_discount_amount=global_discount_amount,
                    total_tax=tax_amount,
                    grand_total=grand_total,
                    notes=notes,
                    terms=terms,
                    status="draft"
                )

                # Save to cloud storage
                estimate_dict = estimate.__dict__.copy()
                estimate_dict["items"] = [item.__dict__ for item in estimate_items]

                saved_id = cloud_data_manager.add_estimate(estimate_dict)

                # Generate PDF
                try:
                    pdf_generator = CloudPDFEstimateGenerator(business_settings)
                    pdf_bytes = pdf_generator.generate_estimate_pdf_bytes(estimate)

                    # Create download button
                    st.success(f"✅ Estimate {saved_id} created successfully!")

                    filename = f"estimate_{saved_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    cloud_file_manager.create_pdf_download_link(pdf_bytes, filename)

                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
                    st.success(f"✅ Estimate {saved_id} saved successfully (PDF generation failed)")

            else:
                st.warning("⚠️ Please add some items to the estimate before saving!")


def view_estimates_page():
    """View and manage estimates"""
    st.title("📋 View Estimates")

    estimates = cloud_data_manager.get_estimates()

    if not estimates:
        st.info("No estimates found. Create your first estimate!")
        return

    # Display estimates
    for estimate in reversed(estimates):  # Show newest first
        with st.expander(f"📄 {estimate['estimate_number']} - {estimate['customer_name']} (₹{estimate['grand_total']:,.2f})"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**Date:** {estimate['date']}")
                st.write(f"**Customer:** {estimate['customer_name']}")
                st.write(f"**Status:** {estimate['status'].title()}")

            with col2:
                st.write(f"**Subtotal:** ₹{estimate['subtotal']:,.2f}")
                st.write(f"**Tax:** ₹{estimate['total_tax']:,.2f}")
                st.write(f"**Total:** ₹{estimate['grand_total']:,.2f}")

            with col3:
                if st.button(f"🔄 Regenerate PDF", key=f"pdf_{estimate['estimate_id']}"):
                    try:
                        # Convert dict back to objects
                        business_settings_dict = cloud_data_manager.get_business_settings()
                        business_settings = BusinessSettings(**business_settings_dict)

                        # Create estimate items
                        estimate_items = [EstimateItem(**item) for item in estimate['items']]
                        estimate['items'] = estimate_items

                        estimate_obj = Estimate(**estimate)

                        # Generate PDF
                        pdf_generator = CloudPDFEstimateGenerator(business_settings)
                        pdf_bytes = pdf_generator.generate_estimate_pdf_bytes(estimate_obj)

                        filename = f"estimate_{estimate['estimate_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        cloud_file_manager.create_pdf_download_link(pdf_bytes, filename)

                    except Exception as e:
                        st.error(f"❌ Error generating PDF: {str(e)}")


def manage_inventory_page():
    """Manage inventory items"""
    st.title("📦 Manage Inventory")

    # Add new item
    with st.expander("➕ Add New Item"):
        col1, col2 = st.columns(2)

        with col1:
            sku = st.text_input("SKU")
            name = st.text_input("Item Name")
            price = st.number_input("Price", min_value=0.0, format="%.2f")

        with col2:
            category = st.text_input("Category")
            tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, value=18.0)
            discount_rate = st.number_input("Default Discount (%)", min_value=0.0, max_value=100.0, value=0.0)

        description = st.text_area("Description")

        if st.button("➕ Add Item"):
            if name and price > 0:
                item_data = {
                    'sku': sku,
                    'name': name,
                    'description': description,
                    'price': price,
                    'tax_rate': tax_rate,
                    'default_discount_rate': discount_rate,
                    'category': category,
                    'unit': 'piece',
                    'stock_quantity': 0,
                    'low_stock_alert': 5,
                    'is_active': True
                }
                cloud_data_manager.add_inventory_item(item_data)
                st.success("✅ Item added successfully!")
                st.rerun()

    # Display existing items
    st.subheader("Current Inventory")
    items = cloud_data_manager.get_inventory_items()

    for item in items:
        with st.expander(f"📦 {item['name']} - ₹{item['price']:,.2f}"):
            st.write(f"**SKU:** {item['sku']}")
            st.write(f"**Description:** {item['description']}")
            st.write(f"**Category:** {item['category']}")
            st.write(f"**Tax Rate:** {item['tax_rate']}%")


def business_settings_page():
    """Manage business settings"""
    st.title("⚙️ Business Settings")

    settings = cloud_data_manager.get_business_settings()

    col1, col2 = st.columns(2)

    with col1:
        business_name = st.text_input("Business Name", value=settings['business_name'])
        business_phone = st.text_input("Phone", value=settings['business_phone'])
        business_gstin = st.text_input("GSTIN", value=settings['business_gstin'])

    with col2:
        business_email = st.text_input("Email", value=settings['business_email'])
        currency_symbol = st.text_input("Currency Symbol", value=settings['currency_symbol'])
        estimate_prefix = st.text_input("Estimate Prefix", value=settings['estimate_prefix'])

    business_address = st.text_area("Address", value=settings['business_address'])
    terms_and_conditions = st.text_area("Terms & Conditions", value=settings['terms_and_conditions'])
    notes_footer = st.text_area("Footer Notes", value=settings['notes_footer'])

    if st.button("💾 Save Settings"):
        updated_settings = {
            'business_name': business_name,
            'business_address': business_address,
            'business_phone': business_phone,
            'business_email': business_email,
            'business_gstin': business_gstin,
            'currency_symbol': currency_symbol,
            'estimate_prefix': estimate_prefix,
            'terms_and_conditions': terms_and_conditions,
            'notes_footer': notes_footer
        }
        cloud_data_manager.update_business_settings(updated_settings)
        st.success("✅ Settings saved successfully!")


def data_management_page():
    """Data import/export for cloud deployment"""
    st.title("💾 Data Management")

    st.info("💡 **Cloud Deployment Note:** Data is stored in session state and will reset when you refresh the page. Use export/import to backup your data.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📤 Export Data")
        st.write("Download all your data as a JSON file for backup.")

        if st.button("📥 Export All Data"):
            json_data = cloud_file_manager.export_data_as_json()
            filename = f"billing_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            st.download_button(
                label="📄 Download Backup File",
                data=json_data,
                file_name=filename,
                mime="application/json"
            )

    with col2:
        st.subheader("📥 Import Data")
        st.write("Upload a previously exported JSON file to restore your data.")

        uploaded_file = st.file_uploader("Choose JSON file", type=['json'])

        if uploaded_file is not None:
            if st.button("📂 Import Data"):
                json_data = uploaded_file.read().decode('utf-8')
                if cloud_file_manager.import_data_from_json(json_data):
                    st.rerun()


def main():
    """Main application function"""
    initialize_app()

    # Sidebar navigation
    st.sidebar.title("🧾 Billing & Estimate Manager")
    st.sidebar.write("**Cloud Deployment Version**")

    # Navigation
    pages = {
        "🏠 Create Estimate": create_estimate_page,
        "📋 View Estimates": view_estimates_page,
        "📦 Manage Inventory": manage_inventory_page,
        "⚙️ Business Settings": business_settings_page,
        "💾 Data Management": data_management_page
    }

    # Page selection
    selected_page = st.sidebar.selectbox("Navigation", list(pages.keys()))

    # Display selected page
    pages[selected_page]()

    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.info(
        "💡 **Cloud Features:**\n"
        "• Session-based data storage\n"
        "• PDF download functionality\n"
        "• Data export/import\n"
        "• No file persistence required"
    )


if __name__ == "__main__":
    main()