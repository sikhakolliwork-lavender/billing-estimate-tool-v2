export interface LineItem {
  item: string;
  quantity: number;
  rate: number;
  discount: number;
  amount: number;
}

export interface InvoicePayload {
  lines: LineItem[];
  globalDiscount: number;
  globalTax: number;
}

export interface InventoryItem {
  id: string;
  name: string;
  price: number;
}

export interface TallyBridgeProps {
  inventory?: InventoryItem[];
  currency_symbol?: string;
}