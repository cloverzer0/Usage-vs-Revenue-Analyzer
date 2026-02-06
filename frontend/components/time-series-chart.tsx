'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TimeSeriesData } from '@/lib/types';
import { formatCurrency, formatDate } from '@/lib/format';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface TimeSeriesChartProps {
  data: TimeSeriesData[];
}

export function TimeSeriesChart({ data }: TimeSeriesChartProps) {
  const chartData = data.map((item) => ({
    ...item,
    date: formatDate(item.date),
  }));

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ dataKey: string; name: string; value: number; color: string; payload: TimeSeriesData }> }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border rounded-lg p-3 shadow-lg">
          <p className="font-medium mb-1">{payload[0]?.payload.date}</p>
          {payload.map((entry) => (
            <p key={entry.dataKey} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {formatCurrency(entry.value)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Revenue vs Usage Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="date"
              className="text-sm"
              tick={{ fill: 'hsl(var(--foreground))' }}
            />
            <YAxis
              className="text-sm"
              tick={{ fill: 'hsl(var(--foreground))' }}
              tickFormatter={(value) => `$${value}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="revenue"
              stroke="hsl(142, 76%, 36%)"
              strokeWidth={2}
              name="Revenue"
              dot={{ r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="usage_cost"
              stroke="hsl(221, 83%, 53%)"
              strokeWidth={2}
              name="Usage Cost"
              dot={{ r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="profit"
              stroke="hsl(262, 83%, 58%)"
              strokeWidth={2}
              name="Profit"
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
