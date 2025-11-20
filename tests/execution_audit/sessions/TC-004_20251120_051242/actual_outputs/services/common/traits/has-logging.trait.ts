import { Logger } from '@nestjs/common';

export interface HasLogging {
  readonly logger: Logger;
  logInfo(message: string, context?: object): void;
  logError(message: string, error: Error, context?: object): void;
  logDebug(message: string, context?: object): void;
}
