'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RefreshCw, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface Connection {
  id: string;
  name: string;
  status: string;
  source_id: string;
  destination_id: string;
}

interface ConnectionStatus {
  status: string;
  last_sync: string | null;
  sync_status: string;
  records_synced: number;
}

export function AirbyteConnections() {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [statuses, setStatuses] = useState<Record<string, ConnectionStatus>>({});
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState<Record<string, boolean>>({});

  const fetchConnections = async () => {
    try {
      const response = await fetch('/api/airbyte/connections');
      const data = await response.json();
      
      if (data.success) {
        setConnections(data.connections);
        
        // Fetch status for each connection
        for (const conn of data.connections) {
          const statusResponse = await fetch(`/api/airbyte/status/${conn.id}`);
          const statusData = await statusResponse.json();
          
          if (statusData.success) {
            setStatuses(prev => ({
              ...prev,
              [conn.id]: statusData.status
            }));
          }
        }
      }
    } catch (error) {
      console.error('Failed to fetch Airbyte connections:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConnections();
  }, []);

  const handleSync = async (connectionId: string) => {
    setSyncing(prev => ({ ...prev, [connectionId]: true }));
    
    try {
      const response = await fetch(`/api/airbyte/sync/${connectionId}`, {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Refresh status after a delay
        setTimeout(() => fetchConnections(), 2000);
      }
    } catch (error) {
      console.error('Sync failed:', error);
    } finally {
      setSyncing(prev => ({ ...prev, [connectionId]: false }));
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { color: string; label: string }> = {
      active: { color: 'bg-green-100 text-green-700', label: 'Active' },
      inactive: { color: 'bg-gray-100 text-gray-700', label: 'Inactive' },
      error: { color: 'bg-red-100 text-red-700', label: 'Error' },
    };

    const variant = variants[status] || variants.inactive;
    return (
      <Badge className={variant.color}>
        {variant.label}
      </Badge>
    );
  };

  const getSyncStatusIcon = (syncStatus: string) => {
    if (syncStatus === 'succeeded') {
      return <CheckCircle2 className="h-4 w-4 text-green-600" />;
    } else if (syncStatus === 'failed') {
      return <XCircle className="h-4 w-4 text-red-600" />;
    } else {
      return <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />;
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Airbyte Data Pipelines</CardTitle>
          <CardDescription>Loading connections...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (connections.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Airbyte Data Pipelines</CardTitle>
          <CardDescription>No connections configured yet</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Configure your API keys in Settings to automatically create Airbyte data pipelines.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Airbyte Data Pipelines</CardTitle>
          <CardDescription>Automated data synchronization</CardDescription>
        </div>
        <Button variant="outline" size="sm" onClick={fetchConnections}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {connections.map((connection) => {
            const status = statuses[connection.id];
            const isSyncing = syncing[connection.id];

            return (
              <div
                key={connection.id}
                className="flex items-center justify-between border rounded-lg p-4"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{connection.name}</span>
                    {getStatusBadge(connection.status)}
                  </div>
                  
                  {status && (
                    <div className="text-sm text-muted-foreground space-y-1">
                      <div className="flex items-center gap-2">
                        {getSyncStatusIcon(status.sync_status)}
                        <span>
                          Last sync: {status.last_sync 
                            ? formatDistanceToNow(new Date(status.last_sync), { addSuffix: true })
                            : 'Never'}
                        </span>
                      </div>
                      {status.records_synced > 0 && (
                        <div>
                          {status.records_synced.toLocaleString()} records synced
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSync(connection.id)}
                  disabled={isSyncing}
                >
                  {isSyncing ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Syncing...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Sync Now
                    </>
                  )}
                </Button>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
