'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatCurrency, formatPercentage } from '@/lib/format';
import { Summary } from '@/lib/types';
import { TrendingUp, DollarSign, Activity, Percent } from 'lucide-react';

interface SummaryCardsProps {
  summary: Summary;
}

export function SummaryCards({ summary }: SummaryCardsProps) {
  const cards = [
    {
      title: 'Total Revenue',
      value: formatCurrency(summary.total_revenue),
      icon: DollarSign,
      color: 'text-green-600',
    },
    {
      title: 'Total Usage Cost',
      value: formatCurrency(summary.total_usage_cost),
      icon: Activity,
      color: 'text-blue-600',
    },
    {
      title: 'Total Profit',
      value: formatCurrency(summary.total_profit),
      icon: TrendingUp,
      color: 'text-purple-600',
    },
    {
      title: 'Profit Margin',
      value: formatPercentage(summary.profit_margin_percentage),
      icon: Percent,
      color: 'text-orange-600',
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <Card key={card.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {card.title}
              </CardTitle>
              <Icon className={`h-4 w-4 ${card.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{card.value}</div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
