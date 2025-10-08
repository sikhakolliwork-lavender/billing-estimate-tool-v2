"""
Full Billing Application - Main Entry Point

This is the main Streamlit application that integrates the tally_bridge component
with our database system for inventory management, customer management, and estimate generation.
"""

# IMPORTANT: Set Tally Bridge to production mode BEFORE any imports
import os
os.environ["TALLY_BRIDGE_RELEASE"] = "1"

import streamlit as st
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, date

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.managers import CustomerManager, InventoryManager, EstimateManager, SettingsManager
from models.models import Customer, InventoryItem, Estimate, EstimateItem, BusinessSettings
from utils.pdf_generator import PDFEstimateGenerator
from utils.email_sender import EmailSender
import tally_bridge

# Page config
st.set_page_config(
    page_title="Billing & Estimate Manager",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .estimate-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_sample_data():
    """Initialize sample inventory items if database is empty"""
    items = InventoryManager.get_all_items()
    if not items:
        sample_items = [
            InventoryItem(
                sku="LAPTOP001",
                name="Gaming Laptop",
                description="High-performance gaming laptop with RTX 4060",
                price=85000.0,
                tax_rate=18.0,
                category="Electronics",
                unit="nos",
                stock_quantity=15,
                is_active=True
            ),
            InventoryItem(
                sku="MOUSE001",
                name="Wireless Mouse",
                description="Ergonomic wireless mouse with RGB lighting",
                price=2500.0,
                tax_rate=18.0,
                category="Accessories",
                unit="nos",
                stock_quantity=50,
                is_active=True
            ),
            InventoryItem(
                sku="KB001",
                name="Mechanical Keyboard",
                description="RGB mechanical keyboard with blue switches",
                price=5500.0,
                tax_rate=18.0,
                category="Accessories",
                unit="nos",
                stock_quantity=25,
                is_active=True
            ),
            InventoryItem(
                sku="MONITOR001",
                name="4K Monitor",
                description="27-inch 4K UHD monitor with HDR support",
                price=35000.0,
                tax_rate=18.0,
                category="Electronics",
                unit="nos",
                stock_quantity=8,
                is_active=True
            ),
            InventoryItem(
                sku="CHAIR001",
                name="Gaming Chair",
                description="Ergonomic gaming chair with lumbar support",
                price=15000.0,
                tax_rate=18.0,
                category="Furniture",
                unit="nos",
                stock_quantity=12,
                is_active=True
            )
        ]

        for item in sample_items:
            InventoryManager.create_item(item)

    # Initialize sample customer if none exist
    customers = CustomerManager.get_all_customers()
    if not customers:
        sample_customer = Customer(
            name="Tech Solutions Pvt Ltd",
            email="contact@techsolutions.com",
            phone="+91 98765 43210",
            address="123 Business Park, Bangalore, Karnataka 560001",
            gstin="29ABCDE1234F1Z5",
            notes="Premium corporate client"
        )
        CustomerManager.create_customer(sample_customer)

def format_currency(amount: float) -> str:
    """Format amount as Indian currency"""
    return f"₹{amount:,.2f}"

def create_estimate_page():
    """Main estimate creation page"""
    st.markdown('<div class="estimate-header"><h1>🧾 Create New Estimate</h1></div>', unsafe_allow_html=True)

    # Initialize sample data
    initialize_sample_data()

    # Get inventory for the component
    inventory_items = InventoryManager.get_all_items(active_only=True)
    inventory_data = []

    for item in inventory_items:
        inventory_data.append({
            "id": item.id,
            "sku": item.sku,
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "tax_rate": item.tax_rate,
            "default_discount_rate": item.default_discount_rate,
            "category": item.category,
            "unit": item.unit,
            "stock_quantity": item.stock_quantity,
            "display_text": item.get_display_text()
        })

    # Sidebar for customer selection
    with st.sidebar:
        st.header("📋 Estimate Details")

        # Customer selection
        customers = CustomerManager.get_all_customers()
        customer_options = ["Select Customer..."] + [f"{c.name} ({c.email})" for c in customers]
        selected_customer_idx = st.selectbox("Select Customer", range(len(customer_options)), format_func=lambda x: customer_options[x])

        selected_customer = None
        if selected_customer_idx > 0:
            selected_customer = customers[selected_customer_idx - 1]

        # Estimate details
        estimate_date = st.date_input("Estimate Date", value=date.today())
        due_date = st.date_input("Due Date", value=date.today())

        # Notes and terms
        notes = st.text_area("Notes", placeholder="Any additional notes for this estimate...")
        terms = st.text_area("Terms & Conditions", value="Payment is due within 30 days from the date of estimate.")

    # Main estimate creation area
    st.subheader("📦 Add Items to Estimate")

    # Show inventory summary
    with st.expander("📊 Current Inventory Summary", expanded=False):
        if inventory_data:
            for item in inventory_data[:5]:  # Show first 5 items
                st.write(f"**{item['display_text']}** - {format_currency(item['price'])} - Stock: {item['stock_quantity']}")
            if len(inventory_data) > 5:
                st.write(f"... and {len(inventory_data) - 5} more items")
        else:
            st.info("No inventory items found. Add items in the Inventory Management section.")

    # Tally Bridge Component
    estimate_data = tally_bridge.tally_bridge(
        inventory=inventory_data,
        currency_symbol="₹",
        key="main_estimate"
    )

    # Process estimate data when received
    if estimate_data and selected_customer:
        st.success("✅ Estimate data received! Processing...")

        # Create estimate object
        settings = SettingsManager.get_settings()
        estimate_number = EstimateManager.get_next_estimate_number()

        # Calculate totals from the component data
        line_items = estimate_data.get('lines', [])
        subtotal = sum(float(line.get('amount', 0)) for line in line_items)

        # Apply global discount if any
        global_discount_rate = float(estimate_data.get('globalDiscount', 0))
        global_discount_amount = subtotal * (global_discount_rate / 100)

        # Calculate tax (simplified - should be per item in real scenario)
        global_tax_rate = float(estimate_data.get('globalTax', 0))
        total_tax = (subtotal - global_discount_amount) * (global_tax_rate / 100)

        grand_total = subtotal - global_discount_amount + total_tax

        # Create estimate
        estimate = Estimate(
            estimate_number=estimate_number,
            customer_id=selected_customer.id,
            customer_name=selected_customer.name,
            customer_email=selected_customer.email,
            customer_address=selected_customer.address,
            customer_gstin=selected_customer.gstin,
            date=str(estimate_date),
            due_date=str(due_date),
            notes=notes,
            terms=terms,
            subtotal=subtotal,
            global_discount_rate=global_discount_rate,
            global_discount_amount=global_discount_amount,
            total_tax=total_tax,
            grand_total=grand_total,
            status="draft"
        )

        # Create estimate items
        estimate_items = []
        for line in line_items:
            item = EstimateItem(
                estimate_id=estimate.estimate_id,
                name=line.get('item', ''),
                quantity=float(line.get('quantity', 1)),
                unit_price=float(line.get('rate', 0)),
                discount_rate=float(line.get('discount', 0)),
                tax_rate=18.0,  # Default GST rate
                line_total=float(line.get('amount', 0))
            )
            estimate_items.append(item)

        estimate.items = estimate_items

        # Save to database
        try:
            estimate_id = EstimateManager.create_estimate(estimate)
            st.success(f"✅ Estimate {estimate_number} created successfully!")
            st.balloons()

            # Show estimate summary and actions
            with st.expander("📄 Estimate Summary & Actions", expanded=True):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Estimate Number:** {estimate_number}")
                    st.write(f"**Customer:** {selected_customer.name}")
                    st.write(f"**Date:** {estimate_date}")
                    st.write(f"**Subtotal:** {format_currency(subtotal)}")
                    if global_discount_amount > 0:
                        st.write(f"**Discount:** -{format_currency(global_discount_amount)} ({global_discount_rate}%)")
                    st.write(f"**Tax:** {format_currency(total_tax)}")
                    st.write(f"**Grand Total:** {format_currency(grand_total)}")

                    st.subheader("Items:")
                    for item in estimate_items:
                        st.write(f"- {item.name}: {item.quantity} × {format_currency(item.unit_price)} = {format_currency(item.line_total)}")

                with col2:
                    st.subheader("📋 Actions")

                    # Generate PDF
                    if st.button("📄 Generate PDF", key="gen_pdf"):
                        with st.spinner("Generating PDF..."):
                            try:
                                settings = SettingsManager.get_settings()
                                pdf_generator = PDFEstimateGenerator(settings)
                                pdf_path = pdf_generator.generate_estimate_pdf(estimate)
                                st.success(f"✅ PDF generated: {pdf_path}")

                                # Offer download
                                with open(pdf_path, "rb") as pdf_file:
                                    st.download_button(
                                        label="💾 Download PDF",
                                        data=pdf_file.read(),
                                        file_name=f"estimate_{estimate_number}.pdf",
                                        mime="application/pdf"
                                    )
                            except Exception as e:
                                st.error(f"❌ Error generating PDF: {str(e)}")

                    # Send Email
                    if st.button("📧 Send Email", key="send_email"):
                        if selected_customer.email:
                            with st.spinner("Sending email..."):
                                try:
                                    settings = SettingsManager.get_settings()

                                    # First generate PDF if not exists
                                    pdf_generator = PDFEstimateGenerator(settings)
                                    pdf_path = pdf_generator.generate_estimate_pdf(estimate)

                                    # Send email
                                    email_sender = EmailSender(settings)
                                    success = email_sender.send_estimate_email(estimate, pdf_path)

                                    if success:
                                        st.success(f"✅ Email sent to {selected_customer.email}")
                                    else:
                                        st.error("❌ Failed to send email. Please check email settings.")
                                except Exception as e:
                                    st.error(f"❌ Error sending email: {str(e)}")
                        else:
                            st.warning("⚠️ Customer email not available")

        except Exception as e:
            st.error(f"❌ Error creating estimate: {str(e)}")

    elif estimate_data and not selected_customer:
        st.warning("⚠️ Please select a customer to create the estimate.")

    # Quick Stats Section - moved to bottom for better layout
    st.markdown("---")
    st.subheader("💡 Quick Stats")

    # Create three columns for metrics
    col1, col2, col3 = st.columns(3)

    # Show some quick stats
    total_items = len(inventory_data)
    low_stock_items = InventoryManager.get_low_stock_items()
    recent_estimates = EstimateManager.get_all_estimates(limit=5)

    # Metrics in columns
    with col1:
        st.metric("Total Inventory Items", total_items)
    with col2:
        st.metric("Low Stock Alerts", len(low_stock_items))
    with col3:
        st.metric("Recent Estimates", len(recent_estimates))

    # Recent estimates
    if recent_estimates:
        st.subheader("📋 Recent Estimates")
        for estimate in recent_estimates:
            with st.container():
                st.write(f"**{estimate.estimate_number}**")
                st.write(f"{estimate.customer_name}")
                st.write(f"{format_currency(estimate.grand_total)} - {estimate.status}")
                st.write("---")

def customer_management_page():
    """Customer management page"""
    st.markdown('<div class="estimate-header"><h1>👥 Customer Management</h1></div>', unsafe_allow_html=True)

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📋 View Customers", "➕ Add Customer", "🔍 Search Customers"])

    with tab1:
        st.subheader("All Customers")
        customers = CustomerManager.get_all_customers()

        if customers:
            # Display customers in a nice table format
            for idx, customer in enumerate(customers):
                with st.expander(f"👤 {customer.name} ({customer.email})", expanded=False):
                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        st.write(f"**Phone:** {customer.phone or 'N/A'}")
                        st.write(f"**GSTIN:** {customer.gstin or 'N/A'}")

                    with col2:
                        st.write(f"**Address:** {customer.address or 'N/A'}")
                        st.write(f"**Notes:** {customer.notes or 'N/A'}")

                    with col3:
                        if st.button(f"✏️ Edit", key=f"edit_{customer.id}"):
                            st.session_state[f"edit_customer_{customer.id}"] = True

                        if st.button(f"🗑️ Delete", key=f"del_{customer.id}"):
                            if CustomerManager.delete_customer(customer.id):
                                st.success("Customer deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete customer")

                    # Edit form (appears when edit is clicked)
                    if st.session_state.get(f"edit_customer_{customer.id}", False):
                        st.write("---")
                        with st.form(f"edit_form_{customer.id}"):
                            new_name = st.text_input("Name", value=customer.name)
                            new_email = st.text_input("Email", value=customer.email)
                            new_phone = st.text_input("Phone", value=customer.phone)
                            new_address = st.text_area("Address", value=customer.address)
                            new_gstin = st.text_input("GSTIN", value=customer.gstin)
                            new_notes = st.text_area("Notes", value=customer.notes)

                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Save Changes"):
                                    updated_customer = Customer(
                                        id=customer.id,
                                        name=new_name,
                                        email=new_email,
                                        phone=new_phone,
                                        address=new_address,
                                        gstin=new_gstin,
                                        notes=new_notes
                                    )
                                    if CustomerManager.update_customer(updated_customer):
                                        st.success("Customer updated!")
                                        st.session_state[f"edit_customer_{customer.id}"] = False
                                        st.rerun()
                                    else:
                                        st.error("Failed to update customer")

                            with col2:
                                if st.form_submit_button("❌ Cancel"):
                                    st.session_state[f"edit_customer_{customer.id}"] = False
                                    st.rerun()
        else:
            st.info("No customers found. Add your first customer using the 'Add Customer' tab.")

    with tab2:
        st.subheader("Add New Customer")
        with st.form("add_customer_form"):
            name = st.text_input("Customer Name*", placeholder="Enter customer name")
            email = st.text_input("Email", placeholder="customer@example.com")
            phone = st.text_input("Phone", placeholder="+91 98765 43210")
            address = st.text_area("Address", placeholder="Full address with city, state, pincode")
            gstin = st.text_input("GSTIN", placeholder="GST Identification Number")
            notes = st.text_area("Notes", placeholder="Any additional notes about the customer")

            if st.form_submit_button("➕ Add Customer"):
                if name:
                    new_customer = Customer(
                        name=name,
                        email=email,
                        phone=phone,
                        address=address,
                        gstin=gstin,
                        notes=notes
                    )
                    try:
                        customer_id = CustomerManager.create_customer(new_customer)
                        st.success(f"✅ Customer '{name}' added successfully!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error adding customer: {str(e)}")
                else:
                    st.error("❌ Customer name is required!")

    with tab3:
        st.subheader("Search Customers")
        search_term = st.text_input("🔍 Search by name or email", placeholder="Type to search...")

        if search_term:
            results = CustomerManager.search_customers(search_term)
            if results:
                st.write(f"Found {len(results)} customer(s):")
                for customer in results:
                    st.write(f"**{customer.name}** - {customer.email} - {customer.phone}")
            else:
                st.info("No customers found matching your search.")

def inventory_management_page():
    """Inventory management page"""
    st.markdown('<div class="estimate-header"><h1>📦 Inventory Management</h1></div>', unsafe_allow_html=True)

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 View Items", "➕ Add Item", "⚠️ Low Stock", "🔍 Search Items"])

    with tab1:
        st.subheader("All Inventory Items")
        items = InventoryManager.get_all_items(active_only=False)

        if items:
            for item in items:
                with st.expander(f"📦 {item.name} ({item.sku}) - {format_currency(item.price)}", expanded=False):
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                    with col1:
                        st.write(f"**Description:** {item.description}")
                        st.write(f"**Category:** {item.category}")
                        st.write(f"**Unit:** {item.unit}")

                    with col2:
                        st.write(f"**Price:** {format_currency(item.price)}")
                        st.write(f"**Tax Rate:** {item.tax_rate}%")

                    with col3:
                        st.write(f"**Stock:** {item.stock_quantity}")
                        st.write(f"**Low Stock Alert:** {item.low_stock_alert}")
                        status_color = "🟢" if item.is_active else "🔴"
                        st.write(f"**Status:** {status_color} {'Active' if item.is_active else 'Inactive'}")

                    with col4:
                        if st.button(f"✏️ Edit", key=f"edit_item_{item.id}"):
                            st.session_state[f"edit_item_{item.id}"] = True

                        if st.button(f"🗑️ Delete", key=f"del_item_{item.id}"):
                            if InventoryManager.delete_item(item.id):
                                st.success("Item deleted!")
                                st.rerun()

                    # Edit form
                    if st.session_state.get(f"edit_item_{item.id}", False):
                        st.write("---")
                        with st.form(f"edit_item_form_{item.id}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                new_sku = st.text_input("SKU", value=item.sku)
                                new_name = st.text_input("Name", value=item.name)
                                new_description = st.text_area("Description", value=item.description)
                                new_category = st.text_input("Category", value=item.category)

                            with col2:
                                new_price = st.number_input("Price", value=float(item.price), min_value=0.0, step=0.01)
                                new_tax_rate = st.number_input("Tax Rate (%)", value=float(item.tax_rate), min_value=0.0, step=0.1)
                                new_stock = st.number_input("Stock Quantity", value=item.stock_quantity, min_value=0)
                                new_low_stock = st.number_input("Low Stock Alert", value=item.low_stock_alert, min_value=0)
                                new_active = st.checkbox("Active", value=item.is_active)

                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Save Changes"):
                                    updated_item = InventoryItem(
                                        id=item.id,
                                        sku=new_sku,
                                        name=new_name,
                                        description=new_description,
                                        price=new_price,
                                        tax_rate=new_tax_rate,
                                        category=new_category,
                                        unit=item.unit,
                                        stock_quantity=new_stock,
                                        low_stock_alert=new_low_stock,
                                        is_active=new_active
                                    )
                                    if InventoryManager.update_item(updated_item):
                                        st.success("Item updated!")
                                        st.session_state[f"edit_item_{item.id}"] = False
                                        st.rerun()

                            with col2:
                                if st.form_submit_button("❌ Cancel"):
                                    st.session_state[f"edit_item_{item.id}"] = False
                                    st.rerun()
        else:
            st.info("No inventory items found. Add your first item using the 'Add Item' tab.")

    with tab2:
        st.subheader("Add New Inventory Item")
        with st.form("add_item_form"):
            col1, col2 = st.columns(2)

            with col1:
                sku = st.text_input("SKU*", placeholder="ITEM001")
                name = st.text_input("Item Name*", placeholder="Enter item name")
                description = st.text_area("Description", placeholder="Item description")
                category = st.text_input("Category", placeholder="Electronics, Furniture, etc.")

            with col2:
                price = st.number_input("Price*", min_value=0.0, step=0.01, value=0.0)
                tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, step=0.1, value=18.0)
                unit = st.selectbox("Unit", ["nos", "kg", "gram", "liter", "meter", "feet", "box", "pack"])
                stock_quantity = st.number_input("Initial Stock", min_value=0, value=0)
                low_stock_alert = st.number_input("Low Stock Alert Level", min_value=0, value=10)

            if st.form_submit_button("➕ Add Item"):
                if sku and name and price >= 0:
                    new_item = InventoryItem(
                        sku=sku,
                        name=name,
                        description=description,
                        price=price,
                        tax_rate=tax_rate,
                        category=category,
                        unit=unit,
                        stock_quantity=stock_quantity,
                        low_stock_alert=low_stock_alert,
                        is_active=True
                    )
                    try:
                        item_id = InventoryManager.create_item(new_item)
                        st.success(f"✅ Item '{name}' added successfully!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error adding item: {str(e)}")
                else:
                    st.error("❌ SKU, name, and price are required!")

    with tab3:
        st.subheader("⚠️ Low Stock Items")
        low_stock_items = InventoryManager.get_low_stock_items()

        if low_stock_items:
            st.warning(f"Found {len(low_stock_items)} items with low stock!")
            for item in low_stock_items:
                st.write(f"🔴 **{item.name}** ({item.sku}) - Stock: {item.stock_quantity} (Alert at: {item.low_stock_alert})")
        else:
            st.success("✅ All items are adequately stocked!")

    with tab4:
        st.subheader("Search Inventory")
        search_term = st.text_input("🔍 Search by name, SKU, or description", placeholder="Type to search...")

        if search_term:
            results = InventoryManager.search_items(search_term, active_only=False)
            if results:
                st.write(f"Found {len(results)} item(s):")
                for item in results:
                    status = "🟢 Active" if item.is_active else "🔴 Inactive"
                    st.write(f"**{item.name}** ({item.sku}) - {format_currency(item.price)} - Stock: {item.stock_quantity} - {status}")
            else:
                st.info("No items found matching your search.")

def dashboard_page():
    """Analytics dashboard page"""
    st.markdown('<div class="estimate-header"><h1>📊 Business Dashboard</h1></div>', unsafe_allow_html=True)

    # Get data for dashboard
    customers = CustomerManager.get_all_customers()
    inventory_items = InventoryManager.get_all_items()
    recent_estimates = EstimateManager.get_all_estimates(limit=10)
    low_stock_items = InventoryManager.get_low_stock_items()

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👥 Total Customers", len(customers))

    with col2:
        st.metric("📦 Inventory Items", len(inventory_items))

    with col3:
        total_revenue = sum(estimate.grand_total for estimate in recent_estimates)
        st.metric("💰 Recent Revenue", format_currency(total_revenue))

    with col4:
        st.metric("⚠️ Low Stock Alerts", len(low_stock_items))

    # Charts and analytics
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Recent Estimates")
        if recent_estimates:
            estimate_data = []
            for estimate in recent_estimates:
                estimate_data.append({
                    "Estimate": estimate.estimate_number,
                    "Customer": estimate.customer_name,
                    "Amount": estimate.grand_total,
                    "Status": estimate.status,
                    "Date": estimate.date
                })

            import pandas as pd
            df = pd.DataFrame(estimate_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No recent estimates found.")

    with col2:
        st.subheader("📊 Estimate Status Distribution")
        if recent_estimates:
            status_counts = {}
            for estimate in recent_estimates:
                status_counts[estimate.status] = status_counts.get(estimate.status, 0) + 1

            import pandas as pd
            status_df = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
            st.bar_chart(status_df.set_index('Status'))
        else:
            st.info("No estimate data available for chart.")

    # Recent activity
    st.subheader("🕒 Recent Activity")
    if recent_estimates:
        for estimate in recent_estimates[:5]:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{estimate.estimate_number}** - {estimate.customer_name}")
                with col2:
                    st.write(format_currency(estimate.grand_total))
                with col3:
                    status_emoji = {"draft": "📝", "sent": "📧", "paid": "✅", "cancelled": "❌"}.get(estimate.status, "📋")
                    st.write(f"{status_emoji} {estimate.status.title()}")
    else:
        st.info("No recent activity to display.")

def settings_page():
    """Business settings page"""
    st.markdown('<div class="estimate-header"><h1>⚙️ Business Settings</h1></div>', unsafe_allow_html=True)

    # Get current settings
    settings = SettingsManager.get_settings()

    # Create tabs for different setting categories
    tab1, tab2, tab3, tab4 = st.tabs(["🏢 Business Info", "🧾 Estimate Settings", "📧 Email Settings", "🧪 Test Features"])

    with tab1:
        st.subheader("Business Information")
        with st.form("business_info_form"):
            business_name = st.text_input("Business Name", value=settings.business_name)
            business_address = st.text_area("Business Address", value=settings.business_address)
            business_phone = st.text_input("Phone", value=settings.business_phone)
            business_email = st.text_input("Email", value=settings.business_email)
            business_gstin = st.text_input("GSTIN", value=settings.business_gstin)

            if st.form_submit_button("💾 Save Business Info"):
                settings.business_name = business_name
                settings.business_address = business_address
                settings.business_phone = business_phone
                settings.business_email = business_email
                settings.business_gstin = business_gstin

                if SettingsManager.update_settings(settings):
                    st.success("✅ Business information updated!")
                else:
                    st.error("❌ Failed to update settings")

    with tab2:
        st.subheader("Estimate Settings")
        with st.form("estimate_settings_form"):
            estimate_prefix = st.text_input("Estimate Prefix", value=settings.estimate_prefix)
            estimate_counter = st.number_input("Next Estimate Number", value=settings.estimate_counter, min_value=1)
            currency_symbol = st.text_input("Currency Symbol", value=settings.currency_symbol)
            default_tax_rate = st.number_input("Default Tax Rate (%)", value=float(settings.default_tax_rate), min_value=0.0, step=0.1)

            terms_and_conditions = st.text_area("Default Terms & Conditions", value=settings.terms_and_conditions, height=100)
            notes_footer = st.text_area("Default Footer Notes", value=settings.notes_footer, height=100)

            if st.form_submit_button("💾 Save Estimate Settings"):
                settings.estimate_prefix = estimate_prefix
                settings.estimate_counter = estimate_counter
                settings.currency_symbol = currency_symbol
                settings.default_tax_rate = default_tax_rate
                settings.terms_and_conditions = terms_and_conditions
                settings.notes_footer = notes_footer

                if SettingsManager.update_settings(settings):
                    st.success("✅ Estimate settings updated!")
                else:
                    st.error("❌ Failed to update settings")

    with tab3:
        st.subheader("Email Configuration")
        st.info("Configure SMTP settings to send estimates via email")

        with st.form("email_settings_form"):
            smtp_server = st.text_input("SMTP Server", value=settings.smtp_server, placeholder="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", value=settings.smtp_port, min_value=1, max_value=65535)
            smtp_username = st.text_input("SMTP Username", value=settings.smtp_username, placeholder="your-email@gmail.com")
            smtp_password = st.text_input("SMTP Password", value=settings.smtp_password, type="password", placeholder="Your app password")

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Email Settings"):
                    settings.smtp_server = smtp_server
                    settings.smtp_port = smtp_port
                    settings.smtp_username = smtp_username
                    settings.smtp_password = smtp_password

                    if SettingsManager.update_settings(settings):
                        st.success("✅ Email settings updated!")
                    else:
                        st.error("❌ Failed to update settings")

            with col2:
                if st.form_submit_button("📧 Test Email"):
                    if smtp_username:
                        try:
                            email_sender = EmailSender(settings)
                            if email_sender.send_test_email(smtp_username):
                                st.success("✅ Test email sent successfully!")
                            else:
                                st.error("❌ Failed to send test email. Check your settings.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("⚠️ Please enter SMTP username first")

    with tab4:
        st.subheader("🧪 Test Features")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Test PDF Generation**")
            if st.button("📄 Generate Sample PDF"):
                try:
                    # Create a sample estimate for testing
                    sample_estimate = Estimate(
                        estimate_number="SAMPLE-0001",
                        customer_name="Sample Customer",
                        customer_email="sample@example.com",
                        customer_address="123 Test Street, Sample City",
                        date=str(datetime.now().date()),
                        due_date=str(datetime.now().date()),
                        subtotal=1000.0,
                        total_tax=180.0,
                        grand_total=1180.0,
                        notes="This is a sample estimate for testing PDF generation.",
                        terms="Sample terms and conditions"
                    )

                    # Add sample items
                    sample_estimate.items = [
                        EstimateItem(
                            name="Sample Product 1",
                            quantity=2,
                            unit_price=300.0,
                            line_total=600.0,
                            tax_rate=18.0
                        ),
                        EstimateItem(
                            name="Sample Product 2",
                            quantity=1,
                            unit_price=400.0,
                            line_total=400.0,
                            tax_rate=18.0
                        )
                    ]

                    pdf_generator = PDFEstimateGenerator(settings)
                    pdf_path = pdf_generator.generate_estimate_pdf(sample_estimate)
                    st.success(f"✅ Sample PDF generated: {pdf_path}")

                    # Offer download
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="💾 Download Sample PDF",
                            data=pdf_file.read(),
                            file_name="sample_estimate.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")

        with col2:
            st.write("**Database Statistics**")
            customers_count = len(CustomerManager.get_all_customers())
            items_count = len(InventoryManager.get_all_items(active_only=False))
            estimates_count = len(EstimateManager.get_all_estimates(limit=1000))

            st.write(f"👥 Customers: {customers_count}")
            st.write(f"📦 Inventory Items: {items_count}")
            st.write(f"🧾 Total Estimates: {estimates_count}")

def main():
    """Main application entry point"""

    # Sidebar navigation
    with st.sidebar:
        st.title("🧾 Billing Manager")

        page = st.radio(
            "Navigate to:",
            ["📝 Create Estimate", "👥 Customers", "📦 Inventory", "📊 Dashboard", "⚙️ Settings"],
            index=0
        )

    # Route to different pages
    if page == "📝 Create Estimate":
        create_estimate_page()
    elif page == "👥 Customers":
        customer_management_page()
    elif page == "📦 Inventory":
        inventory_management_page()
    elif page == "📊 Dashboard":
        dashboard_page()
    elif page == "⚙️ Settings":
        settings_page()

if __name__ == "__main__":
    main()