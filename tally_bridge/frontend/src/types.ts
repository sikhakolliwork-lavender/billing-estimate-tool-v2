export interface LineItem {
  serial: number;
  item: string;
  quantity: number;
  rate: number;
  discount: number;
  amount: number;
}

export interface EstimatePayload {
  lines: LineItem[];
  globalDiscount: number;
  globalTax: number;
}

export interface InventoryItem {
  id: string;
  sku: string;
  name: string;
  description: string;
  price: number;
  tax_rate: number;
  default_discount_rate: number;
  category: string;
  unit: string;
  stock_quantity: number;
  display_text: string;
}

export interface TallyBridgeProps {
  inventory?: InventoryItem[];
  currency_symbol?: string;
}