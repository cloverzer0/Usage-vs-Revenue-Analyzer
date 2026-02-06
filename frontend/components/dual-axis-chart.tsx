'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatCurrency, formatDate, formatNumber } from '@/lib/format';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useState } from 'react';

interface ChartDataPoint {
  date: string;
  usage: number;
  revenue: number;
}

interface DualAxisChartProps {
  data: ChartDataPoint[];
  title?: string;
}

export function DualAxisChart({ data, title = 'Usage vs Revenue Over Time' }: DualAxisChartProps) {
  const [viewBy, setViewBy] = useState<'all' | 'customer' | 'plan' | 'feature'>('all');

  const chartData = data.map((item) => ({
    ...item,
    date: formatDate(item.date),
  }));

  const CustomTooltip = ({ 
    active, 
    payload 
  }: { 
    active?: boolean; 
    payload?: Array<{ 
      dataKey: string; 
      name: string; 
      value: number; 
      color: string;
      payload?: { date: string };
    }> 
  }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border rounded-lg p-3 shadow-lg">
          <p className="font-medium mb-2">{payload[0]?.payload?.date}</p>
          {payload.map((entry) => (
            <p key={entry.dataKey} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {entry.dataKey === 'revenue' 
                ? formatCurrency(entry.value) 
                : formatNumber(entry.value)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="border-2">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{title}</CardTitle>
          <div className="flex gap-2">
            <Button
              variant={viewBy === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewBy('all')}
            >
              All
            </Button>
            <Button
              variant={viewBy === 'customer' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewBy('customer')}
            >
              By Customer
            </Button>
            <Button
              variant={viewBy === 'plan' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewBy('plan')}
            >
              By Plan
            </Button>
            <Button
              variant={viewBy === 'feature' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewBy('feature')}
            >
              By Feature
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={450}>
          <ComposedChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="date"
              className="text-sm"
              tick={{ fill: 'hsl(var(--foreground))' }}
            />
            <YAxis
              yAxisId="left"
              className="text-sm"
              tick={{ fill: 'hsl(var(--foreground))' }}
              tickFormatter={(value) => formatNumber(value)}
              label={{ value: 'Usage Units', angle: -90, position: 'insideLeft' }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              className="text-sm"
              tick={{ fill: 'hsl(var(--foreground))' }}
              tickFormatter={(value) => `$${value}`}
              label={{ value: 'Revenue ($)', angle: 90, position: 'insideRight' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar
              yAxisId="left"
              dataKey="usage"
              fill="hsl(221, 83%, 53%)"
              name="Usage Units"
              opacity={0.6}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="revenue"
              stroke="hsl(142, 76%, 36%)"
              strokeWidth={3}
              name="Revenue"
              dot={{ r: 5 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
        <p className="mt-4 text-sm text-center text-muted-foreground">
          This chart answers: <span className="font-semibold">&ldquo;Are we scaling profitably?&rdquo;</span>
        </p>
      </CardContent>
    </Card>
  );
}
