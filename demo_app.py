import streamlit as st
import sys
import os

# Add the tally_bridge package to the path so we can import it
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import tally_bridge

def main():
    st.set_page_config(
        page_title="Tally Bridge Demo",
        page_icon="⚡",
        layout="wide"
    )

    st.title("⚡ Tally Bridge Component Demo")
    st.markdown("A production-ready Streamlit component for Tally-style invoice input")

    # Sample inventory data (currently unused in the minimal UI but demonstrates the prop)
    sample_inventory = [
        {"id": "1", "name": "Widget A", "price": 10.50},
        {"id": "2", "name": "Widget B", "price": 25.75},
        {"id": "3", "name": "Service C", "price": 100.00},
        {"id": "4", "name": "Product D", "price": 45.25},
    ]

    # Sidebar configuration
    with st.sidebar:
        st.header("Component Configuration")

        currency_symbol = st.selectbox(
            "Currency Symbol",
            ["₹", "$", "€", "£", "¥"],
            index=0
        )

        use_inventory = st.checkbox(
            "Include sample inventory",
            value=True,
            help="Pass inventory data to component (for future enhancement)"
        )

        st.markdown("---")
        st.markdown("### Instructions")
        st.markdown("""
        1. Add items in the embedded UI
        2. Set quantities, rates, and discounts
        3. Adjust global discount/tax
        4. Click **Save Invoice**
        5. See results below!
        """)

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Invoice Input")

        # Call the tally_bridge component
        result = tally_bridge.tally_bridge(
            inventory=sample_inventory if use_inventory else [],
            currency_symbol=currency_symbol,
            key="invoice_input"
        )

    with col2:
        st.subheader("Results")

        if result is not None:
            st.success("✅ Invoice data received!")

            # Display the raw payload
            with st.expander("Raw Payload", expanded=False):
                st.json(result)

            # Calculate and display totals
            lines = result.get("lines", [])
            global_discount = result.get("globalDiscount", 0)
            global_tax = result.get("globalTax", 0)

            if lines:
                # Calculate subtotal from line items
                subtotal = sum(line.get("amount", 0) for line in lines)

                # Apply global discount
                discount_amount = subtotal * (global_discount / 100)
                after_discount = subtotal - discount_amount

                # Apply global tax
                tax_amount = after_discount * (global_tax / 100)
                grand_total = after_discount + tax_amount

                # Display summary
                st.markdown("### 📊 Invoice Summary")

                # Line items table
                if lines:
                    st.markdown("**Line Items:**")
                    for i, line in enumerate(lines, 1):
                        st.markdown(f"""
                        **{i}.** {line.get('item', 'Unnamed Item')}
                        Qty: {line.get('quantity', 0):.2f} × Rate: {currency_symbol}{line.get('rate', 0):.2f}
                        Discount: {line.get('discount', 0):.1f}% = **{currency_symbol}{line.get('amount', 0):.2f}**
                        """)

                # Totals
                st.markdown("---")
                st.markdown(f"""
                **Subtotal:** {currency_symbol}{subtotal:.2f}
                **Global Discount ({global_discount:.1f}%):** -{currency_symbol}{discount_amount:.2f}
                **Global Tax ({global_tax:.1f}%):** +{currency_symbol}{tax_amount:.2f}
                **Grand Total:** {currency_symbol}{grand_total:.2f}
                """)

                # Store in session state for persistence
                st.session_state.last_invoice = result

            else:
                st.warning("No line items in the invoice")
        else:
            st.info("💡 Add items and click 'Save Invoice' in the UI above")

            # Show last saved invoice if available
            if hasattr(st.session_state, 'last_invoice') and st.session_state.last_invoice:
                with st.expander("Last Saved Invoice", expanded=False):
                    st.json(st.session_state.last_invoice)

    # Footer with component info
    st.markdown("---")
    st.markdown("""
    ### About This Component

    **Tally Bridge** is a production-ready Streamlit custom component that provides:
    - React + TypeScript + Vite frontend
    - Proper `setComponentValue` integration (no hacks)
    - Type-safe props and return values
    - Hot-reload development workflow
    - Production build support

    **Data Flow:** iframe → React component → `setComponentValue` → Python
    """)

if __name__ == "__main__":
    main()