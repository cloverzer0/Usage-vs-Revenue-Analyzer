'use client';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { FeatureMetric } from '@/lib/types';
import { formatCurrency, formatPercentage, formatNumber } from '@/lib/format';

interface FeatureMetricsTableProps {
  features: FeatureMetric[];
}

export function FeatureMetricsTable({ features }: FeatureMetricsTableProps) {
  // Sort by revenue descending
  const sortedFeatures = [...features].sort((a, b) => b.revenue - a.revenue);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Feature Performance</CardTitle>
        <CardDescription>
          Breakdown of usage, cost, and revenue by feature
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="font-semibold">Feature</TableHead>
                <TableHead className="text-right font-semibold">
                  Usage Count
                </TableHead>
                <TableHead className="text-right font-semibold">
                  Total Cost
                </TableHead>
                <TableHead className="text-right font-semibold">
                  Revenue
                </TableHead>
                <TableHead className="text-right font-semibold">
                  Profit Margin
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedFeatures.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground">
                    No feature data available
                  </TableCell>
                </TableRow>
              ) : (
                sortedFeatures.map((feature) => (
                  <TableRow key={feature.feature_name}>
                    <TableCell className="font-medium">
                      {feature.feature_name}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatNumber(feature.usage_count)}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(feature.total_cost)}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(feature.revenue)}
                    </TableCell>
                    <TableCell className="text-right">
                      <span
                        className={
                          feature.profit_margin >= 0
                            ? 'text-green-600 font-medium'
                            : 'text-red-600 font-medium'
                        }
                      >
                        {formatPercentage(feature.profit_margin)}
                      </span>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
