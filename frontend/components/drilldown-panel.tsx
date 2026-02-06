'use client';

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatCurrency, formatNumber } from '@/lib/format';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp, AlertCircle } from 'lucide-react';

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

interface TimelineData {
  date: string;
  usage: number;
  revenue: number;
}

interface FeatureUsage {
  feature: string;
  count: number;
  percentage: number;
}

interface DrilldownPanelProps {
  isOpen: boolean;
  onClose: () => void;
  customer: CustomerData | null;
  usageTimeline: TimelineData[];
  revenueTimeline: TimelineData[];
  featureUsage: FeatureUsage[];
}

export function DrilldownPanel({
  isOpen,
  onClose,
  customer,
  usageTimeline,
  revenueTimeline,
  featureUsage,
}: DrilldownPanelProps) {
  if (!customer) return null;

  const getSuggestedAction = () => {
    if (customer.status === 'unprofitable') {
      if (customer.revenuePerUnit < 0.001) {
        return {
          title: 'Increase Pricing',
          description: 'Revenue per unit is extremely low. Consider increasing base price or adding usage-based fees.',
          icon: TrendingUp,
          color: 'text-green-600',
        };
      }
      if (customer.usageLimit && customer.usage > customer.usageLimit * 0.9) {
        return {
          title: 'Add Usage Cap',
          description: 'Customer is approaching usage limits. Consider implementing hard caps or overage fees.',
          icon: AlertCircle,
          color: 'text-orange-600',
        };
      }
    }
    return {
      title: 'Upsell Plan',
      description: 'Customer shows high engagement. They may be ready for a higher-tier plan with better margins.',
      icon: TrendingUp,
      color: 'text-blue-600',
    };
  };

  const action = getSuggestedAction();
  const ActionIcon = action.icon;

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="right" className="w-full sm:max-w-2xl overflow-y-auto">
        <SheetHeader>
          <SheetTitle className="text-2xl">{customer.name}</SheetTitle>
          <SheetDescription>
            Detailed usage and revenue analysis
          </SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{formatNumber(customer.usage)}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {customer.plan || 'Unknown'} Plan
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{formatCurrency(customer.revenue)}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {formatCurrency(customer.revenuePerUnit)}/unit
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Usage Timeline */}
          <Card>
            <CardHeader>
              <CardTitle>Usage Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={usageTimeline}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="usage" 
                    stroke="hsl(221, 83%, 53%)" 
                    strokeWidth={2}
                    name="Usage"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Revenue Timeline */}
          <Card>
            <CardHeader>
              <CardTitle>Revenue Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={revenueTimeline}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(value) => formatCurrency(value as number)} />
                  <Line 
                    type="monotone" 
                    dataKey="revenue" 
                    stroke="hsl(142, 76%, 36%)" 
                    strokeWidth={2}
                    name="Revenue"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Feature Usage */}
          <Card>
            <CardHeader>
              <CardTitle>Feature-Level Usage</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {featureUsage.map((feature) => (
                  <div key={feature.feature}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">{feature.feature}</span>
                      <span className="text-muted-foreground">
                        {formatNumber(feature.count)} ({feature.percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full"
                        style={{ width: `${feature.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Plan Limits */}
          {customer.usageLimit && (
            <Card>
              <CardHeader>
                <CardTitle>Plan Limits vs Actual</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Usage</span>
                    <span className="font-medium">
                      {formatNumber(customer.usage)} / {formatNumber(customer.usageLimit)}
                    </span>
                  </div>
                  <div className="h-3 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        customer.usage > customer.usageLimit * 0.9
                          ? 'bg-red-500'
                          : customer.usage > customer.usageLimit * 0.7
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                      }`}
                      style={{
                        width: `${Math.min((customer.usage / customer.usageLimit) * 100, 100)}%`,
                      }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {((customer.usage / customer.usageLimit) * 100).toFixed(1)}% of limit used
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Suggested Action */}
          <Card className="border-2 border-primary/20 bg-primary/5">
            <CardHeader>
              <div className="flex items-center gap-2">
                <ActionIcon className={`h-5 w-5 ${action.color}`} />
                <CardTitle>Suggested Action</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <h3 className="font-semibold text-lg mb-2">{action.title}</h3>
              <p className="text-sm text-muted-foreground mb-4">{action.description}</p>
              <Button className="w-full">Take Action</Button>
            </CardContent>
          </Card>
        </div>
      </SheetContent>
    </Sheet>
  );
}
