import React, { useEffect, useRef } from 'react';
import { Streamlit, withStreamlitConnection, ComponentProps } from 'streamlit-component-lib';
import { EstimatePayload } from './types';

const TallyBridge: React.FC<ComponentProps> = (props) => {
  const inventory = props.args?.inventory || [];
  const currency_symbol = props.args?.currency_symbol || '₹';
  const messageListenerRef = useRef<(event: MessageEvent) => void>();

  useEffect(() => {
    // Register message listener on mount
    const handleMessage = (event: MessageEvent) => {
      if (event.data && event.data.type === 'TALLY_SAVE') {
        const payload: EstimatePayload = event.data.payload;
        // Send data back to Python via Streamlit
        Streamlit.setComponentValue(payload);
      }
    };

    messageListenerRef.current = handleMessage;
    window.addEventListener('message', handleMessage);

    // Cleanup on unmount
    return () => {
      if (messageListenerRef.current) {
        window.removeEventListener('message', messageListenerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    // Tell Streamlit about our height
    Streamlit.setFrameHeight(700);
  }, []);

  // Create the iframe HTML content
  const iframeContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Tally Estimate UI</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
      margin: 0;
      padding: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
    }
    .container {
      max-width: 1800px;
      margin: 0 auto;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      padding: 20px;
      border-radius: 16px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.1);
      border: 1px solid rgba(255,255,255,0.2);
    }
    .top-stats-bar {
      display: grid;
      grid-template-columns: 1fr 1fr auto auto;
      gap: 20px;
      align-items: center;
      padding: 15px 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 12px;
      margin-bottom: 20px;
      color: white;
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    .stats-section {
      display: flex;
      align-items: center;
      gap: 15px;
    }
    .stat-item {
      text-align: center;
    }
    .stat-label {
      font-size: 11px;
      font-weight: 500;
      opacity: 0.8;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .stat-value {
      font-size: 16px;
      font-weight: 700;
      margin-top: 2px;
    }
    .main-content {
      width: 100%;
    }
    .header {
      text-align: center;
      margin-bottom: 30px;
      color: #2c3e50;
    }
    .header h2 {
      margin: 0 0 10px 0;
      font-size: 28px;
      font-weight: 700;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .header p {
      margin: 0;
      color: #64748b;
      font-size: 16px;
    }
    .form-group {
      margin-bottom: 15px;
    }
    .global-controls {
      display: flex;
      gap: 15px;
      align-items: center;
    }
    .control-input {
      background: rgba(255, 255, 255, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.3);
      border-radius: 6px;
      padding: 8px 12px;
      color: white;
      font-size: 14px;
      width: 80px;
      text-align: center;
    }
    .control-input::placeholder {
      color: rgba(255, 255, 255, 0.7);
    }
    .control-input:focus {
      outline: none;
      border-color: rgba(255, 255, 255, 0.6);
      background: rgba(255, 255, 255, 0.3);
    }
    .control-label {
      font-size: 12px;
      font-weight: 500;
      opacity: 0.9;
      margin-right: 8px;
    }
    label {
      display: block;
      margin-bottom: 5px;
      font-weight: 600;
      color: #34495e;
    }
    input, select {
      width: 100%;
      padding: 10px 14px;
      border: 2px solid #e2e8f0;
      border-radius: 8px;
      font-size: 14px;
      box-sizing: border-box;
      transition: all 0.2s ease;
      background: rgba(255,255,255,0.8);
    }
    input:focus, select:focus {
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      background: rgba(255,255,255,1);
    }
    .line-item {
      display: grid;
      grid-template-columns: 60px 2fr 1fr 1fr 1fr 1fr auto auto;
      gap: 8px;
      align-items: center;
      padding: 15px;
      border: 1px solid #e1e8ed;
      border-radius: 8px;
      margin-bottom: 12px;
      background: linear-gradient(135deg, #ffffff 0%, #f8fafb 100%);
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
      transition: all 0.2s ease;
    }
    .line-item:hover {
      border-color: #3498db;
      box-shadow: 0 4px 12px rgba(52, 152, 219, 0.15);
      transform: translateY(-1px);
    }
    .line-item input {
      margin: 0;
    }
    button {
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
    }
    .btn-primary {
      background: #3498db;
      color: white;
    }
    .btn-success {
      background: #27ae60;
      color: white;
    }
    .btn-danger {
      background: #e74c3c;
      color: white;
    }
    .btn-primary:hover { background: #2980b9; }
    .btn-success:hover { background: #229954; }
    .btn-danger:hover { background: #c0392b; }
    .btn-sm {
      padding: 6px 10px;
      font-size: 12px;
      min-width: 32px;
      border-radius: 6px;
      font-weight: 700;
    }
    .btn-sm:hover {
      transform: scale(1.05);
    }
    .actions {
      display: flex;
      gap: 12px;
    }
    .action-btn {
      padding: 10px 20px;
      font-size: 13px;
      font-weight: 600;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .btn-save {
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: white;
    }
    .btn-clear {
      background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
      color: white;
    }
    .action-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }

    /* Responsive design */
    @media (max-width: 1200px) {
      .top-stats-bar {
        grid-template-columns: 1fr;
        gap: 15px;
        text-align: center;
      }
      .stats-section {
        justify-content: center;
      }
      .global-controls {
        justify-content: center;
      }
      .actions {
        justify-content: center;
      }
    }
    .search-results {
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      background: white;
      border: 1px solid #ddd;
      border-top: none;
      border-radius: 0 0 4px 4px;
      max-height: 200px;
      overflow-y: auto;
      z-index: 1000;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .search-item {
      padding: 10px;
      cursor: pointer;
      border-bottom: 1px solid #f0f0f0;
    }
    .search-item:hover {
      background: #f8f9fa;
    }
    .search-item:last-child {
      border-bottom: none;
    }
    .search-item-name {
      font-weight: 600;
      color: #2c3e50;
    }
    .search-item-details {
      font-size: 12px;
      color: #7f8c8d;
      margin-top: 2px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>⚡ Tally-Style Estimate</h2>
      <p>Add items, set discounts & tax, then save</p>
    </div>

    <div class="top-stats-bar">
      <div class="stats-section">
        <div class="stat-item">
          <div class="stat-label">Subtotal</div>
          <div class="stat-value" id="subtotal">${currency_symbol}0.00</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Discount</div>
          <div class="stat-value" id="discountAmount">${currency_symbol}0.00</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Tax</div>
          <div class="stat-value" id="taxAmount">${currency_symbol}0.00</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Grand Total</div>
          <div class="stat-value" id="grandTotal">${currency_symbol}0.00</div>
        </div>
      </div>

      <div class="global-controls">
        <div>
          <span class="control-label">Discount:</span>
          <input type="number" id="globalDiscount" class="control-input" value="0" min="0" max="100" step="0.01" placeholder="0%" aria-label="Global discount percentage">
        </div>
        <div>
          <span class="control-label">Tax:</span>
          <input type="number" id="globalTax" class="control-input" value="18" min="0" max="100" step="0.01" placeholder="18%" aria-label="Global tax percentage">
        </div>
      </div>

      <div class="actions">
        <button type="button" class="action-btn btn-save" onclick="saveEstimate()" aria-label="Save estimate and send to application">💾 Save</button>
        <button type="button" class="action-btn btn-clear" onclick="clearAll()" aria-label="Clear all estimate data">🗑️ Clear</button>
      </div>
    </div>

    <div class="main-content">
      <div class="form-group">
        <label>Estimate Lines</label>
        <div id="lineItems"></div>
        <button type="button" class="btn-primary" onclick="addLineItem()" aria-label="Add new estimate line item">+ Add Item</button>
      </div>
    </div>
  </div>

  <script>
    const inventory = ${JSON.stringify(inventory)};
    const currencySymbol = "${currency_symbol}";
    let currentLines = [];

    function addLineItem() {
      const container = document.getElementById('lineItems');
      const index = currentLines.length;

      const lineDiv = document.createElement('div');
      lineDiv.className = 'line-item';
      lineDiv.innerHTML = \`
        <input type="text" id="serial-\${index}" placeholder="\${index + 1}" value="\${index + 1}" onchange="updateLine(\${index}, 'serial', this.value)" onkeydown="handleInputKeydown(\${index}, 0, event)" tabindex="\${(index * 7) + 1}" aria-label="Serial number for line \${index + 1}" style="text-align: center; font-weight: 600;">
        <div style="position: relative;">
          <input type="text" id="item-\${index}" placeholder="Type item name or SKU..." onchange="updateLine(\${index}, 'item', this.value)" oninput="showInventorySearch(\${index}, this.value)" onkeydown="handleSearchKeydown(\${index}, event)" autocomplete="off" tabindex="\${(index * 7) + 2}" aria-label="Item search for line \${index + 1}" aria-expanded="false" aria-haspopup="listbox">
          <div id="search-results-\${index}" class="search-results" role="listbox" aria-label="Search results" style="display: none;"></div>
        </div>
        <input type="number" placeholder="Qty" min="0" step="0.01" onchange="updateLine(\${index}, 'quantity', parseFloat(this.value) || 0)" onkeydown="handleInputKeydown(\${index}, 2, event)" tabindex="\${(index * 7) + 3}" aria-label="Quantity for line \${index + 1}">
        <input type="number" placeholder="Rate" min="0" step="0.01" onchange="updateLine(\${index}, 'rate', parseFloat(this.value) || 0)" onkeydown="handleInputKeydown(\${index}, 3, event)" tabindex="\${(index * 7) + 4}" aria-label="Rate for line \${index + 1}">
        <input type="number" placeholder="Disc %" min="0" max="100" step="0.01" onchange="updateLine(\${index}, 'discount', parseFloat(this.value) || 0)" onkeydown="handleInputKeydown(\${index}, 4, event)" tabindex="\${(index * 7) + 5}" aria-label="Discount percentage for line \${index + 1}">
        <input type="number" id="amount-\${index}" placeholder="Amount" readonly style="background: #f8f9fa;" tabindex="-1" aria-label="Calculated amount for line \${index + 1}">
        <button type="button" class="btn-primary btn-sm" onclick="addLineItem()" onkeydown="handleAddButtonKeydown(\${index}, event)" tabindex="\${(index * 7) + 6}" aria-label="Add new line item after line \${index + 1}">+</button>
        <button type="button" class="btn-danger btn-sm" onclick="removeLine(\${index})" onkeydown="handleRemoveButtonKeydown(\${index}, event)" tabindex="\${(index * 7) + 7}" aria-label="Remove line item \${index + 1}">×</button>
      \`;

      container.appendChild(lineDiv);

      currentLines.push({
        serial: index + 1,
        item: '',
        quantity: 0,
        rate: 0,
        discount: 0,
        amount: 0
      });

      calculateTotals();
    }

    function updateLine(index, field, value) {
      if (currentLines[index]) {
        currentLines[index][field] = value;

        // Calculate line amount
        if (field === 'quantity' || field === 'rate' || field === 'discount') {
          const line = currentLines[index];
          const beforeDiscount = line.quantity * line.rate;
          const discountAmount = beforeDiscount * (line.discount / 100);
          line.amount = beforeDiscount - discountAmount;

          // Update readonly amount field using direct ID
          const amountInput = document.getElementById('amount-' + index);
          if (amountInput) {
            amountInput.value = line.amount.toFixed(2);
          }
        }

        calculateTotals();
      }
    }

    function removeLine(index) {
      currentLines.splice(index, 1);
      refreshLineItems();
      calculateTotals();
    }

    function refreshLineItems() {
      const container = document.getElementById('lineItems');
      container.innerHTML = '';
      const tempLines = [...currentLines];
      currentLines = [];

      tempLines.forEach((line, i) => {
        addLineItem();
        const lineDiv = container.children[i];
        const inputs = lineDiv.querySelectorAll('input');
        inputs[0].value = line.serial || (i + 1);
        inputs[1].value = line.item;
        inputs[2].value = line.quantity;
        inputs[3].value = line.rate;
        inputs[4].value = line.discount;
        inputs[5].value = line.amount.toFixed(2);
        currentLines[i] = { ...line };
      });
    }

    function calculateTotals() {
      const subtotal = currentLines.reduce((sum, line) => sum + line.amount, 0);
      const globalDiscount = parseFloat(document.getElementById('globalDiscount').value) || 0;
      const globalTax = parseFloat(document.getElementById('globalTax').value) || 0;

      const discountAmount = subtotal * (globalDiscount / 100);
      const afterDiscount = subtotal - discountAmount;
      const taxAmount = afterDiscount * (globalTax / 100);
      const grandTotal = afterDiscount + taxAmount;

      document.getElementById('subtotal').textContent = currencySymbol + subtotal.toFixed(2);
      document.getElementById('discountAmount').textContent = currencySymbol + discountAmount.toFixed(2);
      document.getElementById('taxAmount').textContent = currencySymbol + taxAmount.toFixed(2);
      document.getElementById('grandTotal').textContent = currencySymbol + grandTotal.toFixed(2);
    }

    function saveEstimate() {
      if (currentLines.length === 0) {
        alert('Please add some items before saving');
        return;
      }

      const payload = {
        lines: currentLines,
        globalDiscount: parseFloat(document.getElementById('globalDiscount').value) || 0,
        globalTax: parseFloat(document.getElementById('globalTax').value) || 0
      };

      // Send to parent component
      window.parent.postMessage({
        type: 'TALLY_SAVE',
        payload: payload
      }, '*');

      alert('Estimate saved! Check the Streamlit app for results.');
    }

    function clearAll() {
      currentLines = [];
      document.getElementById('lineItems').innerHTML = '';
      document.getElementById('globalDiscount').value = '0';
      document.getElementById('globalTax').value = '18';
      calculateTotals();
    }

    // Add listeners to global fields
    document.getElementById('globalDiscount').addEventListener('input', calculateTotals);
    document.getElementById('globalTax').addEventListener('input', calculateTotals);

    function showInventorySearch(index, searchTerm) {
      const resultsDiv = document.getElementById(\`search-results-\${index}\`);
      const inputElement = document.getElementById(\`item-\${index}\`);

      if (!searchTerm || searchTerm.length < 2) {
        resultsDiv.style.display = 'none';
        inputElement.setAttribute('aria-expanded', 'false');
        return;
      }

      // Filter inventory items
      const filtered = inventory.filter(item =>
        item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.description && item.description.toLowerCase().includes(searchTerm.toLowerCase()))
      ).slice(0, 5); // Limit to 5 results

      if (filtered.length === 0) {
        resultsDiv.style.display = 'none';
        inputElement.setAttribute('aria-expanded', 'false');
        return;
      }

      // Build results HTML
      const resultsHTML = filtered.map((item, idx) => \`
        <div class="search-item" onclick="selectInventoryItem(\${index}, \${JSON.stringify(item).replace(/"/g, '&quot;')})" role="option" aria-selected="false" tabindex="-1">
          <div class="search-item-name">\${item.display_text}</div>
          <div class="search-item-details">
            \${currencySymbol}\${item.price.toFixed(2)} • Stock: \${item.stock_quantity}
          </div>
        </div>
      \`).join('');

      resultsDiv.innerHTML = resultsHTML;
      resultsDiv.style.display = 'block';
      inputElement.setAttribute('aria-expanded', 'true');
    }

    function selectInventoryItem(index, item) {
      // Update the item name field with display text
      const itemInput = document.getElementById(\`item-\${index}\`);
      itemInput.value = item.display_text;

      // Update the rate field with item price
      const lineDiv = document.getElementById('lineItems').children[index];
      const rateInput = lineDiv.querySelectorAll('input')[3]; // Rate is the 4th input (after serial)
      const discountInput = lineDiv.querySelectorAll('input')[4]; // Discount is the 5th input

      rateInput.value = item.price.toFixed(2);
      discountInput.value = item.default_discount_rate.toFixed(1); // Set default discount

      // Update the data model
      updateLine(index, 'item', item.display_text);
      updateLine(index, 'rate', item.price);
      updateLine(index, 'discount', item.default_discount_rate);

      // Recalculate the line amount
      // calculateLineAmount(index); // Function removed, calculation handled in updateLine

      // Hide search results
      const resultsDiv = document.getElementById(\`search-results-\${index}\`);
      const inputElement = document.getElementById(\`item-\${index}\`);
      resultsDiv.style.display = 'none';
      inputElement.setAttribute('aria-expanded', 'false');
    }

    // Hide search results when clicking outside
    document.addEventListener('click', function(event) {
      if (!event.target.closest('.line-item')) {
        const searchResults = document.querySelectorAll('.search-results');
        searchResults.forEach(div => {
          div.style.display = 'none';
          // Update aria-expanded for corresponding input
          const index = div.id.replace('search-results-', '');
          const inputElement = document.getElementById(\`item-\${index}\`);
          if (inputElement) {
            inputElement.setAttribute('aria-expanded', 'false');
          }
        });
      }
    });

    let selectedSearchIndex = -1;

    function handleSearchKeydown(index, event) {
      const resultsDiv = document.getElementById(\`search-results-\${index}\`);
      const results = resultsDiv.querySelectorAll('.search-item');

      switch(event.key) {
        case 'ArrowDown':
          event.preventDefault();
          if (results.length > 0) {
            selectedSearchIndex = Math.min(selectedSearchIndex + 1, results.length - 1);
            updateSearchSelection(results);
          }
          break;
        case 'ArrowUp':
          event.preventDefault();
          if (results.length > 0) {
            selectedSearchIndex = Math.max(selectedSearchIndex - 1, -1);
            updateSearchSelection(results);
          }
          break;
        case 'Enter':
          event.preventDefault();
          if (selectedSearchIndex >= 0 && results[selectedSearchIndex]) {
            results[selectedSearchIndex].click();
          }
          break;
        case 'Escape':
          resultsDiv.style.display = 'none';
          selectedSearchIndex = -1;
          document.getElementById(\`item-\${index}\`).setAttribute('aria-expanded', 'false');
          break;
        case 'Tab':
          resultsDiv.style.display = 'none';
          selectedSearchIndex = -1;
          document.getElementById(\`item-\${index}\`).setAttribute('aria-expanded', 'false');
          break;
      }
    }

    function updateSearchSelection(results) {
      results.forEach((result, i) => {
        if (i === selectedSearchIndex) {
          result.style.background = '#e3f2fd';
          result.setAttribute('aria-selected', 'true');
        } else {
          result.style.background = '';
          result.setAttribute('aria-selected', 'false');
        }
      });
    }

    function handleInputKeydown(lineIndex, fieldIndex, event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        // Move to next field or next action
        const nextTabIndex = (lineIndex * 6) + fieldIndex + 2;
        const nextElement = document.querySelector(\`[tabindex="\${nextTabIndex}"]\`);
        if (nextElement) {
          nextElement.focus();
        } else if (fieldIndex === 3) { // Last input field, move to Add button
          const addButton = document.querySelector(\`[tabindex="\${(lineIndex * 6) + 5}"]\`);
          if (addButton) addButton.focus();
        }
      }
    }

    function handleAddButtonKeydown(index, event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        addLineItem();
        // Focus first field of new line
        setTimeout(() => {
          const newLineFirstInput = document.querySelector(\`[tabindex="\${(currentLines.length - 1) * 6 + 1}"]\`);
          if (newLineFirstInput) newLineFirstInput.focus();
        }, 100);
      }
    }

    function handleRemoveButtonKeydown(index, event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        removeLine(index);
      }
    }

    // Initialize with one empty line
    addLineItem();
  </script>
</body>
</html>`;

  return (
    <div style={{ width: '100%', height: '650px' }}>
      <iframe
        srcDoc={iframeContent}
        style={{
          width: '100%',
          height: '100%',
          border: '1px solid #ddd',
          borderRadius: '8px',
        }}
        title="Tally Estimate UI"
      />
    </div>
  );
};

export default withStreamlitConnection(TallyBridge);