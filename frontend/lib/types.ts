export interface FeatureMetric {
  feature_name: string;
  usage_count: number;
  total_cost: number;
  revenue: number;
  profit_margin: number;
}

export interface TimeSeriesData {
  date: string;
  usage_cost: number;
  revenue: number;
  profit: number;
}

export interface Summary {
  total_usage_cost: number;
  total_revenue: number;
  total_profit: number;
  profit_margin_percentage: number;
  date_range: {
    start: string;
    end: string;
  };
}

export interface DashboardData {
  summary: Summary;
  feature_metrics: FeatureMetric[];
  time_series: TimeSeriesData[];
}

export interface HealthCheck {
  status: string;
  openai_configured: boolean;
  stripe_configured: boolean;
}
