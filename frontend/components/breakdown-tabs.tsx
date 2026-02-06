'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { formatCurrency, formatNumber } from '@/lib/format';
import { Badge } from '@/components/ui/badge';

interface CustomerData {
  id: string;
  name: string;
  usage: number;
  revenue: number;
  revenuePerUnit: number;
  status: 'profitable' | 'unprofitable' | 'warning';
}

interface FeatureData {
  name: string;
  usage: number;
  cost: number;
  revenue: number;
  margin: number;
}

interface PlanData {
  name: string;
  customers: number;
  usage: number;
  revenue: number;
  revenuePerUnit: number;
}

interface BreakdownTabsProps {
  customers: CustomerData[];
  features: FeatureData[];
  plans: PlanData[];
  onCustomerClick: (customer: CustomerData) => void;
}

export function BreakdownTabs({ 
  customers, 
  features, 
  plans,
  onCustomerClick 
}: BreakdownTabsProps) {
  const [activeTab, setActiveTab] = useState('customers');

  const getStatusBadge = (status: 'profitable' | 'unprofitable' | 'warning') => {
    const variants = {
      profitable: { label: '🟢 Profitable', className: 'bg-green-100 text-green-800' },
      warning: { label: '🟡 Warning', className: 'bg-yellow-100 text-yellow-800' },
      unprofitable: { label: '🔴 Unprofitable', className: 'bg-red-100 text-red-800' },
    };
    const { label, className } = variants[status];
    return <Badge className={className}>{label}</Badge>;
  };

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle>Breakdown Analysis</CardTitle>
        <CardDescription>Where insights live — click any row to drill down</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="customers">By Customer</TabsTrigger>
            <TabsTrigger value="features">By Feature</TabsTrigger>
            <TabsTrigger value="plans">By Plan</TabsTrigger>
          </TabsList>

          <TabsContent value="customers" className="mt-4">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Customer</TableHead>
                    <TableHead className="text-right">Usage</TableHead>
                    <TableHead className="text-right">Revenue</TableHead>
                    <TableHead className="text-right">Rev / Unit</TableHead>
                    <TableHead className="text-right">Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {customers.map((customer) => (
                    <TableRow
                      key={customer.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => onCustomerClick(customer)}
                    >
                      <TableCell className="font-medium">{customer.name}</TableCell>
                      <TableCell className="text-right">
                        {formatNumber(customer.usage)}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(customer.revenue)}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(customer.revenuePerUnit)}
                      </TableCell>
                      <TableCell className="text-right">
                        {getStatusBadge(customer.status)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          <TabsContent value="features" className="mt-4">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Feature</TableHead>
                    <TableHead className="text-right">Usage</TableHead>
                    <TableHead className="text-right">Cost</TableHead>
                    <TableHead className="text-right">Revenue</TableHead>
                    <TableHead className="text-right">Margin</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {features.map((feature) => (
                    <TableRow key={feature.name}>
                      <TableCell className="font-medium">{feature.name}</TableCell>
                      <TableCell className="text-right">
                        {formatNumber(feature.usage)}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(feature.cost)}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(feature.revenue)}
                      </TableCell>
                      <TableCell className="text-right">
                        <span className={feature.margin < 0 ? 'text-red-600 font-semibold' : 'text-green-600 font-semibold'}>
                          {feature.margin.toFixed(1)}%
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          <TabsContent value="plans" className="mt-4">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Plan</TableHead>
                    <TableHead className="text-right">Customers</TableHead>
                    <TableHead className="text-right">Usage</TableHead>
                    <TableHead className="text-right">Revenue</TableHead>
                    <TableHead className="text-right">Rev / Unit</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {plans.map((plan) => (
                    <TableRow key={plan.name}>
                      <TableCell className="font-medium">{plan.name}</TableCell>
                      <TableCell className="text-right">
                        {formatNumber(plan.customers)}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatNumber(plan.usage)}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(plan.revenue)}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(plan.revenuePerUnit)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
