import { Injectable, Logger } from '@nestjs/common';
import {
  CanManageInventory,
  StockCheckRequest,
  StockCheckResponse,
  ReserveInventoryRequest,
  ReserveInventoryResponse
} from '../../common/interfaces/can-manage-inventory.interface';
import { HasLogging } from '../../common/traits/has-logging.trait';
import { TracksMetrics } from '../../common/traits/tracks-metrics.trait';

/**
 * InventoryAvailabilityService
 * Implements wide inheritance pattern: 3 capabilities (depth=1, width=3)
 * - CanManageInventory (domain capability)
 * - HasLogging (behavior trait)
 * - TracksMetrics (behavior trait)
 */
@Injectable()
export class InventoryAvailabilityService
  implements CanManageInventory, HasLogging, TracksMetrics {

  readonly logger = new Logger(InventoryAvailabilityService.name);

  // ===================================================================
  // CanManageInventory Implementation
  // ===================================================================

  async checkStockAvailability(request: StockCheckRequest): Promise<StockCheckResponse> {
    this.logInfo('Checking stock availability', { items: request.items });
    this.incrementCounter('inventory.stock_checks');

    const unavailableItems = [];
    for (const item of request.items) {
      const stock = await this.getStock(item.productId);
      if (stock < item.quantity) {
        unavailableItems.push({
          productId: item.productId,
          reason: `Insufficient stock: ${stock} available, ${item.quantity} requested`
        });
      }
    }

    return {
      available: unavailableItems.length === 0,
      unavailableItems
    };
  }

  async reserveInventory(request: ReserveInventoryRequest): Promise<ReserveInventoryResponse> {
    this.logInfo('Reserving inventory', { orderId: request.orderId });
    this.incrementCounter('inventory.reservations_created');

    const reservationId = this.generateReservationId();
    const expiresAt = new Date(Date.now() + 15 * 60 * 1000); // 15 minutes

    // Store reservation in database
    await this.storeReservation(reservationId, request.orderId, request.items, expiresAt);

    return { reservationId, expiresAt };
  }

  async releaseInventoryReservation(reservationId: string): Promise<boolean> {
    this.logInfo('Releasing inventory reservation', { reservationId });
    this.incrementCounter('inventory.reservations_released');

    return await this.deleteReservation(reservationId);
  }

  // ===================================================================
  // HasLogging Implementation
  // ===================================================================

  logInfo(message: string, context?: object): void {
    this.logger.log(message, context);
  }

  logError(message: string, error: Error, context?: object): void {
    this.logger.error(message, error.stack, context);
  }

  logDebug(message: string, context?: object): void {
    this.logger.debug(message, context);
  }

  // ===================================================================
  // TracksMetrics Implementation
  // ===================================================================

  incrementCounter(metric: string, value: number = 1): void {
    // Metrics implementation (e.g., Prometheus)
    console.log(`[METRIC] Counter ${metric} += ${value}`);
  }

  recordTiming(metric: string, duration: number): void {
    console.log(`[METRIC] Timing ${metric}: ${duration}ms`);
  }

  setGauge(metric: string, value: number): void {
    console.log(`[METRIC] Gauge ${metric} = ${value}`);
  }

  // ===================================================================
  // Private Helper Methods
  // ===================================================================

  private async getStock(productId: string): Promise<number> {
    // Database query - mock implementation
    return 100;
  }

  private generateReservationId(): string {
    return `res_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async storeReservation(
    reservationId: string,
    orderId: string,
    items: any[],
    expiresAt: Date
  ): Promise<void> {
    // Database insert - mock implementation
  }

  private async deleteReservation(reservationId: string): Promise<boolean> {
    // Database delete - mock implementation
    return true;
  }
}
