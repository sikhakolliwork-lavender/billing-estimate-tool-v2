# 🧾 Billing & Estimate Manager v2

A comprehensive, production-ready billing and estimate management system built with Streamlit, featuring a custom React component for estimate creation, SQLite database, PDF generation, and email functionality.

## ✨ Features

### 🏗️ Core Functionality
- **Estimate Creation**: Interactive Tally-style estimate creation with real-time calculations and serial number tracking
- **Customer Management**: Complete CRUD operations for customer data
- **Inventory Management**: Full inventory system with stock tracking and low-stock alerts
- **Business Settings**: Configurable business information, estimate settings, and email configuration

### 🔧 Advanced Features
- **PDF Generation**: Professional estimate PDFs with Unicode ₹ symbol support and proper text wrapping
- **Email Integration**: Send estimates via SMTP with PDF attachments
- **Real-time Search**: Autocomplete inventory search in estimate creation
- **Analytics Dashboard**: Business insights with charts and metrics
- **Database Management**: SQLite database with optimized queries and indexes

### 🆕 Recent Improvements
- **Serial Number Tracking**: Added serial numbers to line items for better tracking
- **Enhanced PDF Formatting**: Fixed ₹ currency symbol display and improved table text wrapping
- **Estimate Terminology**: Complete migration from "invoice" to "estimate" throughout the application
- **Improved Amount Calculations**: Fixed field mapping issues for accurate real-time calculations
- **Database Schema Updates**: Migrated database schema to support estimate-focused workflow

### 🎯 Production Ready
- **Custom Streamlit Component**: React + TypeScript + Vite frontend with proper component integration
- **Environment Support**: Development and production modes
- **Error Handling**: Comprehensive error handling throughout the application
- **Data Validation**: Form validation and data integrity checks

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for development)
- npm or yarn

### Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd billing-estimate-tool-v2
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install Node.js dependencies (for development):**
```bash
cd tally_bridge/frontend
npm install
cd ../..
```

### Running the Application

#### Production Mode (Recommended)
```bash
# Build the React component
cd tally_bridge/frontend
npm run build
cd ../..

# Set environment variable for production
export TALLY_BRIDGE_RELEASE=1

# Run the Streamlit app
source venv/bin/activate
streamlit run app.py
```

#### Development Mode
```bash
# Terminal 1: Start React dev server
cd tally_bridge/frontend
npm run dev

# Terminal 2: Start Streamlit app
source venv/bin/activate
streamlit run app.py
```

## 📁 Project Structure

```
billing-estimate-tool-v2/
├── app.py                          # Main Streamlit application
├── demo_app.py                     # Component demo
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── data/                          # SQLite database and exports
│   ├── database.db               # SQLite database
│   └── exports/                  # Generated PDFs and exports
├── src/                          # Source code
│   ├── database/                 # Database layer
│   │   ├── __init__.py
│   │   ├── database.py          # Database manager
│   │   └── managers.py          # Data access layer
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── models.py            # Dataclass models
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── pdf_generator.py     # PDF generation
│       └── email_sender.py      # Email functionality
└── tally_bridge/                  # Custom Streamlit component
    ├── __init__.py               # Python wrapper
    └── frontend/                 # React frontend
        ├── package.json
        ├── src/
        │   ├── TallyBridge.tsx  # Main React component
        │   ├── types.ts         # TypeScript types
        │   └── index.ts
        └── dist/                # Built files (production)
```

## 🚀 Quick Start

### Development Mode (Two Terminals)

**Terminal 1: Frontend Dev Server**
```bash
cd frontend
npm install
npm run dev
```

**Terminal 2: Streamlit App**
```bash
pip install streamlit
streamlit run demo_app.py
```

The frontend dev server runs on `http://localhost:3001` and provides hot reload.

### Production Mode

**Build Frontend:**
```bash
cd frontend
npm run build
```

**Run in Release Mode:**
```bash
export TALLY_BRIDGE_RELEASE=1  # Linux/macOS
set TALLY_BRIDGE_RELEASE=1     # Windows
streamlit run demo_app.py
```

## 📦 Dependencies

**Python:**
- `streamlit` >= 1.0.0

**Node.js:**
- React 18+
- TypeScript 5+
- Vite 4+
- streamlit-component-lib 2+

## 💻 Usage

```python
import tally_bridge

# Basic usage for estimate creation
result = tally_bridge.tally_bridge(
    currency_symbol="₹"
)

if result:
    lines = result["lines"]
    global_discount = result["globalDiscount"]
    global_tax = result["globalTax"]

    # Process the estimate data
    for line in lines:
        serial = line["serial"]  # New: Serial number for tracking
        item = line["item"]
        quantity = line["quantity"]
        rate = line["rate"]
        discount = line["discount"]
        amount = line["amount"]
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `inventory` | `List[Dict]` | `[]` | List of inventory items (future use) |
| `currency_symbol` | `str` | `"₹"` | Currency symbol to display |
| `key` | `str` | `None` | Unique component key |

### Return Value

When "Save Estimate" is clicked, returns a dict with:

```python
{
    "lines": [
        {
            "serial": 1,
            "item": "4K Monitor",
            "quantity": 2.0,
            "rate": 35000.00,
            "discount": 5.0,
            "amount": 66500.00
        }
    ],
    "globalDiscount": 10.0,
    "globalTax": 18.0
}
```

Returns `None` when no estimate has been saved yet.

## 🔄 Data Flow

1. **User Input**: User interacts with the iframe UI
2. **Message Passing**: iframe sends `postMessage` to React component
3. **Component Bridge**: React component calls `Streamlit.setComponentValue(payload)`
4. **Python Return**: Python function returns the payload dict

```
Tally UI (iframe) → React Component → setComponentValue → Python
```

## 🛠️ Development Details

### Environment Switching

The component automatically switches between dev and production modes:

- **Dev Mode**: `TALLY_BRIDGE_RELEASE=0` (default)
  - Uses `http://localhost:3001` dev server
  - Enables hot reload
  - Shows React dev tools

- **Production Mode**: `TALLY_BRIDGE_RELEASE=1`
  - Uses built files from `frontend/dist`
  - Optimized bundle
  - No external dependencies

### Frontend Architecture

- **TallyBridge.tsx**: Main React component with message listener
- **types.ts**: TypeScript interfaces for props and payload
- **main.tsx**: React app entry point
- **Vite**: Build tool with React plugin and TypeScript support

### Message Handling

The component registers a single global message listener that:
1. Listens for `{type: "TALLY_SAVE", payload: {...}}` messages
2. Validates the payload structure
3. Calls `Streamlit.setComponentValue(payload)` to send data to Python
4. Cleans up the listener on component unmount

## 🎨 UI Features

- **Clean Design**: Minimal, professional interface
- **Real-time Calculations**: Totals update as you type
- **Responsive Layout**: Works on different screen sizes
- **Form Validation**: Prevents saving empty invoices
- **User Feedback**: Success messages and visual cues

## 🧪 Testing the Component

1. **Start Dev Servers**: Run both frontend dev server and Streamlit
2. **Add Line Items**: Click "+ Add Item" and fill in details
3. **Set Global Values**: Adjust discount and tax percentages
4. **Save Invoice**: Click "💾 Save Invoice" button
5. **Check Results**: See the payload appear in Streamlit

## 🐛 Troubleshooting

**Frontend dev server not connecting:**
- Ensure `npm run dev` is running on port 3001
- Check for firewall/proxy issues
- Verify `http://localhost:3001` is accessible

**Component not updating:**
- Clear browser cache
- Restart Streamlit server
- Check browser console for errors

**Build fails:**
- Run `npm install` in frontend directory
- Check Node.js version (requires 16+)
- Verify all dependencies are installed

## 📋 Changelog

### v2.1.0 - Latest Updates (September 2024)

**✨ New Features:**
- Added serial number tracking for line items in estimates
- Enhanced PDF generation with Unicode ₹ symbol support
- Improved table text wrapping for long item descriptions
- Complete migration from "invoice" to "estimate" terminology

**🐛 Bug Fixes:**
- Fixed currency symbol (₹) display issues in PDF generation
- Resolved amount calculation field mapping problems
- Fixed table formatting and layout issues in PDFs
- Corrected input field indexing after adding serial numbers

**🔧 Technical Improvements:**
- Database schema migration from invoice_prefix to estimate_prefix
- Enhanced Unicode font support with multiple fallback options
- Improved PDF table styling and formatting
- Better error handling and validation

**📊 Testing:**
- Added comprehensive PDF generation tests
- Created large estimate tests (10+ items)
- Verified currency symbol display across different scenarios

### v2.0.0 - Initial Release
- Basic estimate creation and management
- Customer and inventory management
- PDF generation and email integration
- Streamlit + React component architecture

## 📄 License

This project is provided as-is for demonstration purposes.

## 🤝 Contributing

This is a self-contained example component. Feel free to:
- Fork and modify for your needs
- Use as a template for other components
- Extract patterns for your own projects

---

**Built with ❤️ using React, TypeScript, Vite, and Streamlit**