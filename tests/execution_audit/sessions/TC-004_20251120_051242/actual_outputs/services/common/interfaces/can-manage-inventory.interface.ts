/**
 * Interface: CanManageInventory
 * Provider: InventoryAvailabilityService
 * Generated from ICD: can_manage_inventory_icd.json
 *
 * Inventory management capabilities - check availability, reserve, release
 */

export interface StockCheckRequest {
  items: Array<{ productId: string; quantity: number }>;
}

export interface StockCheckResponse {
  available: boolean;
  unavailableItems: Array<{ productId: string; reason: string }>;
}

export interface ReserveInventoryRequest {
  orderId: string;
  items: Array<{ productId: string; quantity: number }>;
}

export interface ReserveInventoryResponse {
  reservationId: string;
  expiresAt: Date;
}

/**
 * Capability-based interface for inventory management operations
 */
export interface CanManageInventory {
  /**
   * Check if requested items are in stock
   */
  checkStockAvailability(request: StockCheckRequest): Promise<StockCheckResponse>;

  /**
   * Reserve items for this order (temporary hold)
   */
  reserveInventory(request: ReserveInventoryRequest): Promise<ReserveInventoryResponse>;

  /**
   * Release reserved items (on failure or timeout)
   */
  releaseInventoryReservation(reservationId: string): Promise<boolean>;
}
