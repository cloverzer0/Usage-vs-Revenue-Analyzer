'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Settings, LogOut } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

interface NavigationProps {
  onDateRangeChange: (range: string) => void;
  onEnvironmentChange: (env: string) => void;
  onOpenSettings: () => void;
}

export function Navigation({ onDateRangeChange, onEnvironmentChange, onOpenSettings }: NavigationProps) {
  const [dateRange, setDateRange] = useState('30');
  const [environment, setEnvironment] = useState('production');
  const { user, logout } = useAuth();

  const handleDateRangeChange = (value: string) => {
    setDateRange(value);
    onDateRangeChange(value);
  };

  const handleEnvironmentChange = (value: string) => {
    setEnvironment(value);
    onEnvironmentChange(value);
  };

  return (
    <div className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center px-8 max-w-full">
        <div className="flex items-center flex-shrink-0">
          <h1 className="text-lg font-semibold whitespace-nowrap">Usage vs Revenue Analyzer</h1>
        </div>

        <div className="flex items-center gap-2 ml-auto">
          {user && (
            <span className="text-sm text-muted-foreground mr-2">
              {user.full_name || user.username}
            </span>
          )}
        </div>

        <div className="flex items-center gap-6 ml-4 flex-shrink-0">
          <div className="flex items-center gap-2">
            <Select value={dateRange} onValueChange={handleDateRangeChange}>
              <SelectTrigger className="w-[140px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7">Last 7 days</SelectItem>
                <SelectItem value="30">Last 30 days</SelectItem>
                <SelectItem value="90">Last 90 days</SelectItem>
                <SelectItem value="custom">Custom range</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            <Select value={environment} onValueChange={handleEnvironmentChange}>
              <SelectTrigger className="w-[120px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="production">Production</SelectItem>
                <SelectItem value="staging">Staging</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button variant="outline" size="sm" onClick={onOpenSettings}>
            <Settings className="mr-2 h-4 w-4" />
            <span className="font-medium">Settings</span>
          </Button>

          <Button variant="ghost" size="sm" onClick={logout}>
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>
    </div>
  );
}
