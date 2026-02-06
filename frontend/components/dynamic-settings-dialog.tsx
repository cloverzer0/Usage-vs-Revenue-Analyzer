'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle2, XCircle, Loader2, Plus, Trash2, Settings } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';

interface ServiceConfig {
  id?: string;
  service_type: string;
  service_name: string;
  api_key: string;
  account_id?: string;
  org_id?: string;
  additional_config?: Record<string, string>;
  status?: 'active' | 'inactive' | 'pending';
}

interface ServiceDefinition {
  id: string;
  name: string;
  category: 'usage' | 'revenue';
  description: string;
  fields: Array<{
    key: string;
    label: string;
    type: 'text' | 'password';
    required: boolean;
    placeholder?: string;
  }>;
}

const USAGE_SERVICES: ServiceDefinition[] = [
  {
    id: 'openai',
    name: 'OpenAI',
    category: 'usage',
    description: 'AI API usage tracking',
    fields: [
      { key: 'api_key', label: 'API Key', type: 'password', required: true, placeholder: 'sk-...' },
      { key: 'org_id', label: 'Organization ID', type: 'text', required: false, placeholder: 'org-...' },
    ],
  },
  {
    id: 'anthropic',
    name: 'Anthropic',
    category: 'usage',
    description: 'Claude API usage tracking',
    fields: [
      { key: 'api_key', label: 'API Key', type: 'password', required: true, placeholder: 'sk-ant-...' },
    ],
  },
  {
    id: 'aws',
    name: 'AWS CloudWatch',
    category: 'usage',
    description: 'AWS resource usage metrics',
    fields: [
      { key: 'access_key_id', label: 'Access Key ID', type: 'text', required: true },
      { key: 'secret_access_key', label: 'Secret Access Key', type: 'password', required: true },
      { key: 'region', label: 'Region', type: 'text', required: true, placeholder: 'us-east-1' },
    ],
  },
  {
    id: 'datadog',
    name: 'Datadog',
    category: 'usage',
    description: 'Infrastructure monitoring and usage',
    fields: [
      { key: 'api_key', label: 'API Key', type: 'password', required: true },
      { key: 'app_key', label: 'Application Key', type: 'password', required: true },
      { key: 'site', label: 'Site', type: 'text', required: false, placeholder: 'datadoghq.com' },
    ],
  },
  {
    id: 'custom-usage',
    name: 'Custom Usage API',
    category: 'usage',
    description: 'Any usage tracking API',
    fields: [
      { key: 'api_key', label: 'API Key', type: 'password', required: true },
      { key: 'base_url', label: 'Base URL', type: 'text', required: true, placeholder: 'https://api.example.com' },
      { key: 'account_id', label: 'Account ID', type: 'text', required: false },
    ],
  },
];

const REVENUE_SERVICES: ServiceDefinition[] = [
  {
    id: 'stripe',
    name: 'Stripe',
    category: 'revenue',
    description: 'Payment processing and subscription billing',
    fields: [
      { key: 'api_key', label: 'Secret Key', type: 'password', required: true, placeholder: 'sk_test_...' },
      { key: 'account_id', label: 'Account ID', type: 'text', required: false, placeholder: 'acct_...' },
    ],
  },
  {
    id: 'chargebee',
    name: 'Chargebee',
    category: 'revenue',
    description: 'Subscription management and recurring billing',
    fields: [
      { key: 'api_key', label: 'API Key', type: 'password', required: true },
      { key: 'site', label: 'Site Name', type: 'text', required: true, placeholder: 'your-site' },
    ],
  },
  {
    id: 'paddle',
    name: 'Paddle',
    category: 'revenue',
    description: 'Payment processing for SaaS',
    fields: [
      { key: 'api_key', label: 'API Key', type: 'password', required: true },
      { key: 'vendor_id', label: 'Vendor ID', type: 'text', required: true },
    ],
  },
  {
    id: 'recurly',
    name: 'Recurly',
    category: 'revenue',
    description: 'Subscription billing management',
    fields: [
      { key: 'api_key', label: 'API Key', type: 'password', required: true },
      { key: 'subdomain', label: 'Subdomain', type: 'text', required: true, placeholder: 'your-company' },
    ],
  },
  {
    id: 'braintree',
    name: 'Braintree',
    category: 'revenue',
    description: 'PayPal payment platform',
    fields: [
      { key: 'merchant_id', label: 'Merchant ID', type: 'text', required: true },
      { key: 'public_key', label: 'Public Key', type: 'text', required: true },
      { key: 'private_key', label: 'Private Key', type: 'password', required: true },
    ],
  },
  {
    id: 'custom-revenue',
    name: 'Custom Revenue API',
    category: 'revenue',
    description: 'Any billing/revenue tracking API',
    fields: [
      { key: 'api_key', label: 'API Key', type: 'password', required: true },
      { key: 'base_url', label: 'Base URL', type: 'text', required: true, placeholder: 'https://api.example.com' },
      { key: 'account_id', label: 'Account/Tenant ID', type: 'text', required: false },
    ],
  },
];

const ALL_SERVICES = [...USAGE_SERVICES, ...REVENUE_SERVICES];

interface DynamicSettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function DynamicSettingsDialog({ open, onOpenChange }: DynamicSettingsDialogProps) {
  const [services, setServices] = useState<ServiceConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  
  // Add service form state
  const [selectedCategory, setSelectedCategory] = useState<'usage' | 'revenue'>('usage');
  const [selectedServiceType, setSelectedServiceType] = useState<string>('');
  const [serviceName, setServiceName] = useState('');
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  useEffect(() => {
    if (open) {
      loadServices();
    }
  }, [open]);

  const loadServices = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/services');
      const data = await response.json();
      if (data.services) {
        setServices(data.services);
      }
    } catch (error) {
      console.error('Failed to load services:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleServiceTypeChange = (type: string) => {
    setSelectedServiceType(type);
    const service = ALL_SERVICES.find(s => s.id === type);
    if (service) {
      setServiceName(service.name);
      setSelectedCategory(service.category);
      // Reset form data
      const newFormData: Record<string, string> = {};
      service.fields.forEach(field => {
        newFormData[field.key] = '';
      });
      setFormData(newFormData);
    }
  };

  const getServicesByCategory = (category: 'usage' | 'revenue') => {
    return category === 'usage' ? USAGE_SERVICES : REVENUE_SERVICES;
  };

  const handleFieldChange = (key: string, value: string) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setResult(null);

    try {
      const response = await fetch('/api/test-service', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_type: selectedServiceType,
          credentials: formData,
        }),
      });

      const data = await response.json();
      setResult({
        success: response.ok,
        message: data.message || (response.ok ? 'Connection successful!' : 'Connection failed')
      });
    } catch {
      setResult({
        success: false,
        message: 'Failed to test connection. Please check your network.'
      });
    } finally {
      setTesting(false);
    }
  };

  const handleAddService = async () => {
    setSaving(true);
    setResult(null);

    try {
      const response = await fetch('/api/services', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_type: selectedServiceType,
          service_name: serviceName,
          service_category: selectedCategory,
          credentials: formData,
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setResult({ success: true, message: data.message || 'Service added successfully!' });
        setTimeout(() => {
          setShowAddForm(false);
          setSelectedServiceType('');
          setServiceName('');
          setFormData({});
          setResult(null);
          loadServices();
        }, 1500);
      } else {
        setResult({ success: false, message: data.detail || 'Failed to add service' });
      }
    } catch {
      setResult({ success: false, message: 'Error adding service' });
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteService = async (serviceId: string) => {
    try {
      const response = await fetch(`/api/services/${serviceId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        loadServices();
      }
    } catch (error) {
      console.error('Failed to delete service:', error);
    }
  };

  const selectedService = ALL_SERVICES.find(s => s.id === selectedServiceType);
  const availableServices = getServicesByCategory(selectedCategory);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Service Integrations</DialogTitle>
          <DialogDescription>
            Connect usage and revenue services to automatically sync data through Airbyte pipelines.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Configured Services */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium">Configured Services</h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowAddForm(true)}
                disabled={showAddForm}
              >
                <Plus className="mr-2 h-4 w-4" />
                Add Service
              </Button>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : services.length === 0 && !showAddForm ? (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-sm text-muted-foreground text-center">
                    No services configured yet. Click &quot;Add Service&quot; to get started.
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-2">
                {services.map((service) => (
                  <Card key={service.id}>
                    <CardContent className="flex items-center justify-between p-4">
                      <div className="flex items-center gap-3">
                        <Settings className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{service.service_name}</p>
                          <p className="text-xs text-muted-foreground">{service.service_type}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={service.status === 'active' ? 'default' : 'secondary'}>
                          {service.status || 'active'}
                        </Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => service.id && handleDeleteService(service.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Add Service Form */}
          {showAddForm && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Add New Service</CardTitle>
                <CardDescription>Configure a usage or revenue service integration</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Category Selection */}
                <div className="space-y-2">
                  <Label>Service Category</Label>
                  <Select value={selectedCategory} onValueChange={(val) => {
                    setSelectedCategory(val as 'usage' | 'revenue');
                    setSelectedServiceType('');
                  }}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="usage">
                        <div>
                          <div className="font-medium">Usage Services</div>
                          <div className="text-xs text-muted-foreground">Track API calls, compute, storage usage</div>
                        </div>
                      </SelectItem>
                      <SelectItem value="revenue">
                        <div>
                          <div className="font-medium">Revenue Services</div>
                          <div className="text-xs text-muted-foreground">Track payments, subscriptions, billing</div>
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Service Type Selection */}
                <div className="space-y-2">
                  <Label>Service Type</Label>
                  <Select value={selectedServiceType} onValueChange={handleServiceTypeChange}>
                    <SelectTrigger>
                      <SelectValue placeholder={`Select a ${selectedCategory} service`} />
                    </SelectTrigger>
                    <SelectContent>
                      {availableServices.map((service) => (
                        <SelectItem key={service.id} value={service.id}>
                          <div>
                            <div className="font-medium">{service.name}</div>
                            <div className="text-xs text-muted-foreground">{service.description}</div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Dynamic Fields */}
                {selectedService && (
                  <>
                    <div className="space-y-2">
                      <Label>Custom Name (Optional)</Label>
                      <Input
                        value={serviceName}
                        onChange={(e) => setServiceName(e.target.value)}
                        placeholder={selectedService.name}
                      />
                    </div>

                    {selectedService.fields.map((field) => (
                      <div key={field.key} className="space-y-2">
                        <Label>
                          {field.label}
                          {field.required && <span className="text-red-500 ml-1">*</span>}
                        </Label>
                        <Input
                          type={field.type}
                          value={formData[field.key] || ''}
                          onChange={(e) => handleFieldChange(field.key, e.target.value)}
                          placeholder={field.placeholder}
                          required={field.required}
                        />
                      </div>
                    ))}

                    {result && (
                      <Alert variant={result.success ? 'default' : 'destructive'}>
                        {result.success ? (
                          <CheckCircle2 className="h-4 w-4" />
                        ) : (
                          <XCircle className="h-4 w-4" />
                        )}
                        <AlertDescription>{result.message}</AlertDescription>
                      </Alert>
                    )}

                    <div className="flex gap-2 pt-2">
                      <Button
                        variant="outline"
                        onClick={handleTestConnection}
                        disabled={testing || saving}
                      >
                        {testing ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Testing...
                          </>
                        ) : (
                          'Test Connection'
                        )}
                      </Button>
                      <Button onClick={handleAddService} disabled={testing || saving}>
                        {saving ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Adding...
                          </>
                        ) : (
                          'Add Service'
                        )}
                      </Button>
                      <Button
                        variant="ghost"
                        onClick={() => {
                          setShowAddForm(false);
                          setSelectedCategory('usage');
                          setSelectedServiceType('');
                          setServiceName('');
                          setFormData({});
                          setResult(null);
                        }}
                      >
                        Cancel
                      </Button>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
