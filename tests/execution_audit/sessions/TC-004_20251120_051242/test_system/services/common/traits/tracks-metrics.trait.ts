export interface TracksMetrics {
  incrementCounter(metric: string, value?: number): void;
  recordTiming(metric: string, duration: number): void;
  setGauge(metric: string, value: number): void;
}
