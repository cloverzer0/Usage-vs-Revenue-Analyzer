'use client';

import { useEffect, useState } from 'react';
import { DashboardData } from '@/lib/types';
import { fetchDashboardData, fetchHealthCheck } from '@/lib/api';
import { Navigation } from '@/components/navigation';
import { KPICards } from '@/components/kpi-cards';
import { DualAxisChart } from '@/components/dual-axis-chart';
import { BreakdownTabs } from '@/components/breakdown-tabs';
import { DrilldownPanel } from '@/components/drilldown-panel';
import { InsightsSection } from '@/components/insights-section';
import { DynamicSettingsDialog } from '@/components/dynamic-settings-dialog';
import { AirbyteConnections } from '@/components/airbyte-connections';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle, Loader2 } from 'lucide-react';
import { subDays } from 'date-fns';
import { useAuth } from '@/lib/auth-context';

interface CustomerData {
  id: string;
  name: string;
  usage: number;
  revenue: number;
  revenuePerUnit: number;
  status: 'profitable' | 'unprofitable' | 'warning';
  plan?: string;
  usageLimit?: number;
}

export default function DashboardPage() {
  const { user, isLoading: authLoading } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerData | null>(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [customers, setCustomers] = useState<CustomerData[]>([]);

  const loadData = async (startDate?: string, endDate?: string) => {
    try {
      setLoading(true);
      setError(null);
      const dashboardData = await fetchDashboardData(startDate, endDate);
      setData(dashboardData);
      
      // Fetch real customer data
      const customersResponse = await fetch('/api/customers');
      if (customersResponse.ok) {
        const customersData = await customersResponse.json();
        const transformedCustomers = customersData.customers.map((c: { id: string; name: string; usage: number; revenue: number; revenue_per_unit: number; plan?: string }) => ({
          id: c.id,
          name: c.name,
          usage: c.usage,
          revenue: c.revenue,
          revenuePerUnit: c.revenue_per_unit,
          status: c.revenue < c.usage * 0.001 ? 'unprofitable' : c.revenue_per_unit < 0.08 ? 'warning' : 'profitable',
          plan: c.plan,
          usageLimit: c.usage * 1.2,
        }));
        setCustomers(transformedCustomers);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleDateRangeChange = (range: string) => {
    const endDate = new Date();
    let startDate = endDate;
    
    switch (range) {
      case '7':
        startDate = subDays(endDate, 7);
        break;
      case '30':
        startDate = subDays(endDate, 30);
        break;
      case '90':
        startDate = subDays(endDate, 90);
        break;
      default:
        startDate = subDays(endDate, 30);
    }

    loadData(startDate.toISOString().split('T')[0], endDate.toISOString().split('T')[0]);
  };

  const handleEnvironmentChange = (env: string) => {
    console.log('Environment changed to:', env);
    // In production, this would filter data by environment
  };

  const handleCustomerClick = (customer: CustomerData) => {
    setSelectedCustomer(customer);
    setIsPanelOpen(true);
  };

  // Transform data for new components
  const getKPIData = () => {
    if (!data) return null;
    
    const totalUsage = data.feature_metrics.reduce((sum, f) => sum + f.usage_count, 0);
    const unprofitableFeatures = data.feature_metrics.filter(f => f.profit_margin < 0);
    const unprofitableUsage = unprofitableFeatures.reduce((sum, f) => sum + f.usage_count, 0);
    
    return {
      totalRevenue: data.summary.total_revenue,
      totalUsageUnits: totalUsage,
      revenuePerUnit: totalUsage > 0 ? data.summary.total_revenue / totalUsage : 0,
      unprofitableUsagePercent: totalUsage > 0 ? (unprofitableUsage / totalUsage) * 100 : 0,
    };
  };

  const getChartData = () => {
    if (!data) return [];
    return data.time_series.map(item => ({
      date: item.date,
      usage: item.usage_cost * 10000, // Approximate usage from cost
      revenue: item.revenue,
    }));
  };

  const getPlanData = () => {
    if (!customers.length) return [];
    
    // Aggregate customers by plan
    const planMap = new Map<string, { customers: number; usage: number; revenue: number }>();
    
    customers.forEach(customer => {
      const plan = customer.plan || 'Unknown';
      const existing = planMap.get(plan) || { customers: 0, usage: 0, revenue: 0 };
      planMap.set(plan, {
        customers: existing.customers + 1,
        usage: existing.usage + customer.usage,
        revenue: existing.revenue + customer.revenue,
      });
    });
    
    return Array.from(planMap.entries()).map(([name, data]) => ({
      name,
      customers: data.customers,
      usage: data.usage,
      revenue: data.revenue,
      revenuePerUnit: data.usage > 0 ? data.revenue / data.usage : 0,
    }));
  };

  const getInsights = () => {
    if (!data) return [];
    
    const insights = [];
    const legacyFeatures = data.feature_metrics.filter(f => f.feature_name.includes('v1') || f.feature_name.includes('legacy'));
    const costlyFeatures = data.feature_metrics.filter(f => f.profit_margin < -10);
    
    if (legacyFeatures.length > 0) {
      const legacyUsage = legacyFeatures.reduce((sum, f) => sum + f.usage_count, 0);
      const totalUsage = data.feature_metrics.reduce((sum, f) => sum + f.usage_count, 0);
      const percentage = ((legacyUsage / totalUsage) * 100).toFixed(1);
      
      insights.push({
        id: 'legacy-usage',
        type: 'warning' as const,
        category: 'usage' as const,
        title: 'High Legacy Feature Usage',
        description: `${percentage}% of API usage comes from customers on legacy plans. Consider migration strategy.`,
        metric: `${legacyUsage.toLocaleString()} legacy API calls`,
      });
    }
    
    if (costlyFeatures.length > 0) {
      insights.push({
        id: 'costly-features',
        type: 'critical' as const,
        category: 'feature' as const,
        title: 'Unprofitable Features Detected',
        description: `${costlyFeatures.length} feature(s) cost more to run than they generate in revenue.`,
        metric: `Total loss: ${data.summary.total_profit < 0 ? Math.abs(data.summary.total_profit).toFixed(2) : '0.00'}`,
      });
    }
    
    const highUsageCustomers = customers.filter(c => c.usageLimit && c.usage > c.usageLimit * 0.9);
    if (highUsageCustomers.length > 0) {
      insights.push({
        id: 'usage-threshold',
        type: 'warning' as const,
        category: 'customer' as const,
        title: 'Fair-Use Thresholds Exceeded',
        description: `${highUsageCustomers.length} customer(s) exceed fair-use thresholds. Review usage caps and pricing.`,
        metric: `${highUsageCustomers.map(c => c.name).join(', ')}`,
      });
    }
    
    return insights;
  };

  const checkHealth = async () => {
    try {
      const health = await fetchHealthCheck();
      setHealthCheck(health);
    } catch (err) {
      console.error('Health check failed:', err);
    }
  };

  useEffect(() => {
    // Only load data after auth is verified
    if (!authLoading && user) {
      checkHealth();
      loadData();
    }
  }, [authLoading, user]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const kpiData = getKPIData();
  const chartData = getChartData();
  const plans = getPlanData();
  const insights = getInsights();

  return (
    <div className="min-h-screen bg-background">
      <Navigation
        onDateRangeChange={handleDateRangeChange}
        onEnvironmentChange={handleEnvironmentChange}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      <DynamicSettingsDialog
        open={isSettingsOpen}
        onOpenChange={setIsSettingsOpen}
      />

      <div className="container mx-auto p-6 space-y-6">
        <AirbyteConnections />

        {kpiData && <KPICards data={kpiData} />}

        <DualAxisChart data={chartData} />

        <BreakdownTabs
          customers={customers}
          features={data.feature_metrics.map(f => ({
            name: f.feature_name,
            usage: f.usage_count,
            cost: f.total_cost,
            revenue: f.revenue,
            margin: f.profit_margin,
          }))}
          plans={plans}
          onCustomerClick={handleCustomerClick}
        />

        <InsightsSection insights={insights} />
      </div>

      {selectedCustomer && data && (
        <DrilldownPanel
          isOpen={isPanelOpen}
          onClose={() => setIsPanelOpen(false)}
          customer={selectedCustomer}
          usageTimeline={data.time_series.map(item => ({
            date: item.date,
            usage: item.usage_cost * 100,
            revenue: item.revenue / customers.length,
          }))}
          revenueTimeline={data.time_series.map(item => ({
            date: item.date,
            usage: 0,
            revenue: item.revenue / customers.length,
          }))}
          featureUsage={data.feature_metrics.slice(0, 5).map(f => {
            const totalUsage = data.feature_metrics.reduce((sum, feature) => sum + feature.usage_count, 0);
            const percentage = totalUsage > 0 ? (f.usage_count / totalUsage) * 100 : 0;
            return {
              feature: f.feature_name,
              count: f.usage_count,
              percentage: Math.round(percentage),
            };
          })}
        />
      )}
    </div>
  );
}
