import os
import streamlit.components.v1 as components
from typing import List, Dict, Any, Optional

# Get the directory of this file
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Check if we're in release mode
_RELEASE = os.environ.get("TALLY_BRIDGE_RELEASE", "0") == "1"

if _RELEASE:
    # Production mode: use built files
    _component_func = components.declare_component(
        "tally_bridge",
        path=os.path.join(_CURRENT_DIR, "frontend", "dist"),
    )
else:
    # Development mode: use dev server
    _component_func = components.declare_component(
        "tally_bridge",
        url="http://localhost:3001",
    )


def tally_bridge(
    inventory: Optional[List[Dict[str, Any]]] = None,
    currency_symbol: str = "₹",
    key: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Create a Tally-style invoice input component.

    Parameters
    ----------
    inventory : list of dict, optional
        List of inventory items with fields: 'id', 'sku', 'name', 'description',
        'price', 'tax_rate', 'category', 'unit'. Used for autocomplete and validation.
    currency_symbol : str, default "₹"
        Currency symbol to display in the UI.
    key : str, optional
        Unique key for this component instance.

    Returns
    -------
    dict or None
        When Save Invoice is clicked, returns a dict with:
        - lines: list of line items with fields: item, quantity, rate, discount, amount
        - globalDiscount: global discount percentage
        - globalTax: global tax percentage
        Returns None when no invoice has been saved yet.

    Examples
    --------
    >>> import tally_bridge
    >>>
    >>> # Basic usage
    >>> result = tally_bridge.tally_bridge(currency_symbol="$")
    >>> if result:
    >>>     st.write("Invoice data:", result)
    >>>
    >>> # With inventory (for future use)
    >>> inventory = [
    >>>     {"id": "1", "name": "Widget A", "price": 10.0},
    >>>     {"id": "2", "name": "Widget B", "price": 25.0},
    >>> ]
    >>> result = tally_bridge.tally_bridge(
    >>>     inventory=inventory,
    >>>     currency_symbol="€"
    >>> )
    """
    if inventory is None:
        inventory = []

    # Call the component function
    component_value = _component_func(
        inventory=inventory,
        currency_symbol=currency_symbol,
        key=key,
        default=None,
    )

    return component_value