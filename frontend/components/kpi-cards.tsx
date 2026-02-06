'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatCurrency, formatNumber, formatPercentage } from '@/lib/format';
import { DollarSign, Activity, TrendingUp, AlertTriangle } from 'lucide-react';

interface KPIData {
  totalRevenue: number;
  totalUsageUnits: number;
  revenuePerUnit: number;
  unprofitableUsagePercent: number;
}

interface KPICardsProps {
  data: KPIData;
}

export function KPICards({ data }: KPICardsProps) {
  const cards = [
    {
      title: 'Total Revenue',
      value: formatCurrency(data.totalRevenue),
      subtitle: 'Stripe-based',
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Total Usage Units',
      value: formatNumber(data.totalUsageUnits),
      subtitle: 'API calls / events',
      icon: Activity,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Revenue per Unit',
      value: formatCurrency(data.revenuePerUnit),
      subtitle: 'Derived metric',
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Unprofitable Usage',
      value: formatPercentage(data.unprofitableUsagePercent),
      subtitle: 'Flag metric',
      icon: AlertTriangle,
      color: data.unprofitableUsagePercent > 20 ? 'text-red-600' : 'text-orange-600',
      bgColor: data.unprofitableUsagePercent > 20 ? 'bg-red-50' : 'bg-orange-50',
    },
  ];

  return (
    <div className="space-y-2">
      <h2 className="text-sm font-medium text-muted-foreground">Executive Summary</h2>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <Card key={card.title} className="border-2">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {card.title}
                </CardTitle>
                <div className={`rounded-full p-2 ${card.bgColor}`}>
                  <Icon className={`h-4 w-4 ${card.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${card.color}`}>
                  {card.value}
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  {card.subtitle}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
