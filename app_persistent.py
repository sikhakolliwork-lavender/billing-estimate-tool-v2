"""
Persistent Cloud Billing & Estimate Manager with Google Drive Integration

This version provides permanent data persistence using Google Drive API,
maintaining data across sessions and deployments.
"""

import streamlit as st
import os
from datetime import datetime
from typing import Optional, Dict, Any

# Set Tally Bridge to production mode for cloud deployment
os.environ["TALLY_BRIDGE_RELEASE"] = "1"

# Set up imports
try:
    from src.utils.google_drive_storage import drive_persistent_manager
    from src.utils.pdf_generator import PDFEstimateGenerator
    from src.database.managers import CustomerManager, InventoryManager, EstimateManager, SettingsManager
    from src.database.database import DatabaseManager
    from src.models.models import BusinessSettings, Estimate, EstimateItem
    import tally_bridge
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()


def initialize_app():
    """Initialize the Streamlit app with proper configuration"""
    st.set_page_config(
        page_title="Billing & Estimate Manager - Persistent",
        page_icon="🧾",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def setup_google_drive_auth():
    """Setup Google Drive authentication"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("☁️ Google Drive Sync")

    if 'drive_authenticated' not in st.session_state:
        st.session_state.drive_authenticated = False
        st.session_state.db_synced = False

    # Check if already authenticated
    if drive_persistent_manager.authenticate():
        st.session_state.drive_authenticated = True

    if st.session_state.drive_authenticated:
        st.sidebar.success("✅ Google Drive Connected")

        # Sync status
        if st.session_state.get('db_synced', False):
            st.sidebar.info("📊 Database Synced")
        else:
            st.sidebar.warning("⚠️ Database Not Synced")

        # Manual sync buttons
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("⬇️ Sync From Drive", help="Download latest data from Google Drive"):
                sync_from_drive()

        with col2:
            if st.button("⬆️ Sync To Drive", help="Upload current data to Google Drive"):
                sync_to_drive()

        # Auto-sync toggle
        auto_sync = st.sidebar.checkbox("🔄 Auto-sync", value=st.session_state.get('auto_sync', False))
        st.session_state.auto_sync = auto_sync

    else:
        st.sidebar.error("❌ Google Drive Not Connected")

        # Handle OAuth authentication
        if 'oauth_code' not in st.session_state:
            # Show authentication instructions
            with st.sidebar.expander("🔐 Setup Google Drive Authentication"):
                st.markdown("""
                **Two Options:**

                **Option 1: Service Account (Recommended for deployment)**
                1. Go to [Google Cloud Console](https://console.cloud.google.com/)
                2. Create a new project or select existing
                3. Enable Google Drive API
                4. Create Service Account credentials
                5. Download JSON key file
                6. Add to Streamlit secrets as `google_drive`

                **Option 2: OAuth (For personal use)**
                1. Create OAuth 2.0 credentials
                2. Add to Streamlit secrets as `google_oauth`
                3. Click 'Get Auth URL' below
                """)

            # OAuth flow
            auth_url = drive_persistent_manager.get_oauth_url()
            if auth_url:
                st.sidebar.markdown(f"[🔐 Authorize Google Drive Access]({auth_url})")

                auth_code = st.sidebar.text_input("Enter authorization code:")
                if auth_code and st.sidebar.button("✅ Authenticate"):
                    if drive_persistent_manager.handle_oauth(auth_code):
                        st.session_state.drive_authenticated = True
                        st.session_state.oauth_code = auth_code
                        st.rerun()
                    else:
                        st.sidebar.error("Authentication failed!")


def sync_from_drive():
    """Sync database from Google Drive"""
    with st.spinner("Downloading data from Google Drive..."):
        db_path = drive_persistent_manager.sync_from_drive()
        if db_path:
            # Initialize database manager with the downloaded database
            st.session_state.db_path = db_path
            st.session_state.db_synced = True

            # Initialize database manager
            if 'db_manager' not in st.session_state:
                st.session_state.db_manager = DatabaseManager(db_path)

            st.success("✅ Data synced from Google Drive!")
        else:
            st.error("❌ Failed to sync from Google Drive")


def sync_to_drive():
    """Sync database to Google Drive"""
    if 'db_path' in st.session_state:
        with st.spinner("Uploading data to Google Drive..."):
            if drive_persistent_manager.sync_to_drive():
                st.success("✅ Data synced to Google Drive!")
            else:
                st.error("❌ Failed to sync to Google Drive")
    else:
        st.warning("⚠️ No local database to sync")


def get_database_manager():
    """Get or create database manager"""
    if 'db_manager' not in st.session_state:
        if st.session_state.get('drive_authenticated', False):
            # Try to sync from drive first
            db_path = drive_persistent_manager.sync_from_drive()
            if db_path:
                st.session_state.db_path = db_path
                st.session_state.db_manager = DatabaseManager(db_path)
                st.session_state.db_synced = True
            else:
                st.error("❌ Could not sync database from Google Drive")
                return None
        else:
            st.warning("⚠️ Google Drive not connected. Using temporary storage.")
            return None

    return st.session_state.db_manager


def create_estimate_page():
    """Create estimate page with persistent storage"""
    st.title("🧾 Create New Estimate")

    # Ensure database is available
    db_manager = get_database_manager()
    if not db_manager:
        st.error("❌ Database not available. Please connect Google Drive first.")
        return

    # Get business settings
    try:
        settings = SettingsManager.get_settings()
    except Exception as e:
        st.error(f"Error loading business settings: {e}")
        return

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
        estimate_number = st.text_input("Estimate Number", value=EstimateManager.get_next_estimate_number())

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
                           value=settings.terms_and_conditions,
                           placeholder="Payment terms...")

    # Get inventory items for the component
    try:
        inventory_items = InventoryManager.get_all_items()
    except Exception as e:
        st.error(f"Error loading inventory: {e}")
        inventory_items = []

    # Tally Bridge Component
    st.subheader("💼 Line Items")

    # Convert inventory to the format expected by tally_bridge
    inventory_for_component = [
        {
            "id": item.id,
            "name": item.name,
            "price": item.price,
            "tax_rate": item.tax_rate,
            "discount_rate": item.default_discount_rate
        }
        for item in inventory_items
    ]

    # Render the tally bridge component
    result = tally_bridge.tally_bridge(
        inventory=inventory_for_component,
        currency_symbol=settings.currency_symbol,
        key="estimate_creator_persistent"
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

                # Save to database
                try:
                    saved_id = EstimateManager.create_estimate(estimate)

                    # Generate PDF
                    pdf_generator = PDFEstimateGenerator(settings)
                    pdf_path = pdf_generator.generate_estimate_pdf(estimate)

                    st.success(f"✅ Estimate {saved_id} created successfully!")

                    # Provide download link for PDF
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="📄 Download PDF",
                            data=pdf_file.read(),
                            file_name=f"estimate_{saved_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )

                    # Auto-sync to Google Drive if enabled
                    if st.session_state.get('auto_sync', False):
                        sync_to_drive()

                except Exception as e:
                    st.error(f"❌ Error saving estimate: {str(e)}")

            else:
                st.warning("⚠️ Please add some items to the estimate before saving!")


def view_estimates_page():
    """View and manage estimates"""
    st.title("📋 View Estimates")

    db_manager = get_database_manager()
    if not db_manager:
        st.error("❌ Database not available. Please connect Google Drive first.")
        return

    try:
        estimates = EstimateManager.get_all_estimates()
    except Exception as e:
        st.error(f"Error loading estimates: {e}")
        return

    if not estimates:
        st.info("No estimates found. Create your first estimate!")
        return

    # Display estimates
    for estimate in estimates:
        with st.expander(f"📄 {estimate.estimate_number} - {estimate.customer_name} (₹{estimate.grand_total:,.2f})"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**Date:** {estimate.date}")
                st.write(f"**Customer:** {estimate.customer_name}")
                st.write(f"**Status:** {estimate.status.title()}")

            with col2:
                st.write(f"**Subtotal:** ₹{estimate.subtotal:,.2f}")
                st.write(f"**Tax:** ₹{estimate.total_tax:,.2f}")
                st.write(f"**Total:** ₹{estimate.grand_total:,.2f}")

            with col3:
                if st.button(f"🔄 Regenerate PDF", key=f"pdf_{estimate.estimate_id}"):
                    try:
                        settings = SettingsManager.get_settings()
                        pdf_generator = PDFEstimateGenerator(settings)
                        pdf_path = pdf_generator.generate_estimate_pdf(estimate)

                        with open(pdf_path, "rb") as pdf_file:
                            st.download_button(
                                label="📄 Download PDF",
                                data=pdf_file.read(),
                                file_name=f"estimate_{estimate.estimate_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                key=f"download_{estimate.estimate_id}"
                            )

                    except Exception as e:
                        st.error(f"❌ Error generating PDF: {str(e)}")


def manage_inventory_page():
    """Manage inventory items"""
    st.title("📦 Manage Inventory")

    db_manager = get_database_manager()
    if not db_manager:
        st.error("❌ Database not available. Please connect Google Drive first.")
        return

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
                try:
                    from src.models.models import InventoryItem
                    item = InventoryItem(
                        sku=sku,
                        name=name,
                        description=description,
                        price=price,
                        tax_rate=tax_rate,
                        default_discount_rate=discount_rate,
                        category=category,
                        unit='piece',
                        stock_quantity=0,
                        low_stock_alert=5,
                        is_active=True
                    )
                    item_id = InventoryManager.create_item(item)
                    st.success(f"✅ Item added successfully! ID: {item_id}")

                    # Auto-sync to Google Drive if enabled
                    if st.session_state.get('auto_sync', False):
                        sync_to_drive()

                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error adding item: {str(e)}")

    # Display existing items
    st.subheader("Current Inventory")
    try:
        items = InventoryManager.get_all_items()
    except Exception as e:
        st.error(f"Error loading inventory: {e}")
        return

    for item in items:
        with st.expander(f"📦 {item.name} - ₹{item.price:,.2f}"):
            st.write(f"**SKU:** {item.sku}")
            st.write(f"**Description:** {item.description}")
            st.write(f"**Category:** {item.category}")
            st.write(f"**Tax Rate:** {item.tax_rate}%")


def business_settings_page():
    """Manage business settings"""
    st.title("⚙️ Business Settings")

    db_manager = get_database_manager()
    if not db_manager:
        st.error("❌ Database not available. Please connect Google Drive first.")
        return

    try:
        settings = SettingsManager.get_settings()
    except Exception as e:
        st.error(f"Error loading settings: {e}")
        return

    col1, col2 = st.columns(2)

    with col1:
        business_name = st.text_input("Business Name", value=settings.business_name)
        business_phone = st.text_input("Phone", value=settings.business_phone)
        business_gstin = st.text_input("GSTIN", value=settings.business_gstin)

    with col2:
        business_email = st.text_input("Email", value=settings.business_email)
        currency_symbol = st.text_input("Currency Symbol", value=settings.currency_symbol)
        estimate_prefix = st.text_input("Estimate Prefix", value=settings.estimate_prefix)

    business_address = st.text_area("Address", value=settings.business_address)
    terms_and_conditions = st.text_area("Terms & Conditions", value=settings.terms_and_conditions)
    notes_footer = st.text_area("Footer Notes", value=settings.notes_footer)

    if st.button("💾 Save Settings"):
        try:
            updated_settings = BusinessSettings(
                business_name=business_name,
                business_address=business_address,
                business_phone=business_phone,
                business_email=business_email,
                business_gstin=business_gstin,
                currency_symbol=currency_symbol,
                estimate_prefix=estimate_prefix,
                terms_and_conditions=terms_and_conditions,
                notes_footer=notes_footer
            )
            SettingsManager.update_settings(updated_settings)
            st.success("✅ Settings saved successfully!")

            # Auto-sync to Google Drive if enabled
            if st.session_state.get('auto_sync', False):
                sync_to_drive()

        except Exception as e:
            st.error(f"❌ Error saving settings: {str(e)}")


def main():
    """Main application function"""
    initialize_app()

    # Sidebar navigation
    st.sidebar.title("🧾 Billing & Estimate Manager")
    st.sidebar.write("**Persistent Cloud Version**")

    # Google Drive authentication setup
    setup_google_drive_auth()

    # Navigation
    pages = {
        "🏠 Create Estimate": create_estimate_page,
        "📋 View Estimates": view_estimates_page,
        "📦 Manage Inventory": manage_inventory_page,
        "⚙️ Business Settings": business_settings_page
    }

    # Page selection
    selected_page = st.sidebar.selectbox("Navigation", list(pages.keys()))

    # Display selected page
    pages[selected_page]()

    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.info(
        "💡 **Persistent Features:**\n"
        "• Google Drive cloud storage\n"
        "• Permanent data persistence\n"
        "• Auto-sync capabilities\n"
        "• Full SQLite database\n"
        "• Same features as local app"
    )


if __name__ == "__main__":
    main()