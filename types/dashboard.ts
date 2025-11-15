export interface Metric {
  label: string;
  value: string;
  trend: string;
  positive?: boolean;
}

export interface ChannelMetric {
  label: string;
  value: string;
  delta: string;
}

