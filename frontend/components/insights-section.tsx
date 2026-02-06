'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle, TrendingDown, Users, DollarSign } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface Insight {
  id: string;
  type: 'warning' | 'info' | 'critical';
  category: 'usage' | 'revenue' | 'customer' | 'feature';
  title: string;
  description: string;
  metric?: string;
}

interface InsightsSectionProps {
  insights: Insight[];
}

export function InsightsSection({ insights }: InsightsSectionProps) {
  const getIcon = (category: string) => {
    switch (category) {
      case 'usage':
        return <TrendingDown className="h-4 w-4" />;
      case 'customer':
        return <Users className="h-4 w-4" />;
      case 'revenue':
        return <DollarSign className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  const getVariant = (type: string): 'default' | 'destructive' => {
    return type === 'critical' ? 'destructive' : 'default';
  };

  const getSeverityBadge = (type: string) => {
    const styles = {
      critical: 'bg-red-100 text-red-800',
      warning: 'bg-yellow-100 text-yellow-800',
      info: 'bg-blue-100 text-blue-800',
    };
    return (
      <Badge className={styles[type as keyof typeof styles]}>
        {type.toUpperCase()}
      </Badge>
    );
  };

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle>Insights & Flags</CardTitle>
        <p className="text-sm text-muted-foreground">
          Rule-based analysis of your usage and revenue patterns
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {insights.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <AlertCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No insights at this time</p>
            <p className="text-sm">All metrics are within normal ranges</p>
          </div>
        ) : (
          insights.map((insight) => (
            <Alert key={insight.id} variant={getVariant(insight.type)}>
              <div className="flex items-start gap-3">
                <div className="mt-0.5">{getIcon(insight.category)}</div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <AlertTitle className="mb-0">{insight.title}</AlertTitle>
                    {getSeverityBadge(insight.type)}
                  </div>
                  <AlertDescription className="text-sm">
                    {insight.description}
                  </AlertDescription>
                  {insight.metric && (
                    <p className="text-sm font-mono font-semibold mt-2">
                      {insight.metric}
                    </p>
                  )}
                </div>
              </div>
            </Alert>
          ))
        )}
      </CardContent>
    </Card>
  );
}
