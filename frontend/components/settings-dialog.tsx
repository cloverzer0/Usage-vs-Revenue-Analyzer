'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface SettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function SettingsDialog({ open, onOpenChange }: SettingsDialogProps) {
  const [openaiKey, setOpenaiKey] = useState('');
  const [openaiOrg, setOpenaiOrg] = useState('');
  const [stripeKey, setStripeKey] = useState('');
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleTestConnection = async (service: 'openai' | 'stripe') => {
    setTesting(true);
    setTestResult(null);

    try {
      const response = await fetch('/api/test-connection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service,
          credentials: service === 'openai' 
            ? { api_key: openaiKey, org_id: openaiOrg }
            : { api_key: stripeKey }
        }),
      });

      const data = await response.json();
      setTestResult({
        success: response.ok,
        message: data.message || (response.ok ? 'Connection successful!' : 'Connection failed')
      });
    } catch {
      setTestResult({
        success: false,
        message: 'Failed to test connection. Please check your network.'
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          openai: { api_key: openaiKey, org_id: openaiOrg },
          stripe: { api_key: stripeKey }
        }),
      });

      if (response.ok) {
        setTestResult({ success: true, message: 'Settings saved successfully!' });
        setTimeout(() => onOpenChange(false), 1500);
      } else {
        setTestResult({ success: false, message: 'Failed to save settings' });
      }
    } catch {
      setTestResult({ success: false, message: 'Error saving settings' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Integration Settings</DialogTitle>
          <DialogDescription>
            Configure your API keys. Airbyte will automatically create data pipelines for continuous syncing.
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="openai" className="mt-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="openai">OpenAI</TabsTrigger>
            <TabsTrigger value="stripe">Stripe</TabsTrigger>
          </TabsList>

          <TabsContent value="openai" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="openai-key">API Key</Label>
              <Input
                id="openai-key"
                type="password"
                placeholder="sk-..."
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="openai-org">Organization ID (optional)</Label>
              <Input
                id="openai-org"
                placeholder="org-..."
                value={openaiOrg}
                onChange={(e) => setOpenaiOrg(e.target.value)}
              />
            </div>
            <Button
              variant="outline"
              onClick={() => handleTestConnection('openai')}
              disabled={!openaiKey || testing}
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
          </TabsContent>

          <TabsContent value="stripe" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="stripe-key">Secret Key</Label>
              <Input
                id="stripe-key"
                type="password"
                placeholder="sk_test_..."
                value={stripeKey}
                onChange={(e) => setStripeKey(e.target.value)}
              />
            </div>
            <Button
              variant="outline"
              onClick={() => handleTestConnection('stripe')}
              disabled={!stripeKey || testing}
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
          </TabsContent>
        </Tabs>

        {testResult && (
          <Alert variant={testResult.success ? 'default' : 'destructive'}>
            {testResult.success ? (
              <CheckCircle2 className="h-4 w-4" />
            ) : (
              <XCircle className="h-4 w-4" />
            )}
            <AlertDescription>{testResult.message}</AlertDescription>
          </Alert>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={saving || (!openaiKey && !stripeKey)}>
            {saving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              'Save Settings'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
