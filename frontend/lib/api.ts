import { DashboardData, HealthCheck, FeatureMetric, Summary, TimeSeriesData } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function getAuthHeaders(): HeadersInit {
  // Only access localStorage on the client side
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
}

export async function fetchHealthCheck(): Promise<HealthCheck> {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error('Failed to fetch health check');
  }
  return response.json();
}

export async function fetchDashboardData(
  startDate?: string,
  endDate?: string
): Promise<DashboardData> {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const url = `${API_BASE_URL}/api/dashboard${params.toString() ? `?${params.toString()}` : ''}`;
  const response = await fetch(url, {
    headers: getAuthHeaders()
  });
  
  if (!response.ok) {
    if (response.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
      }
      throw new Error('Unauthorized');
    }
    throw new Error('Failed to fetch dashboard data');
  }
  
  return response.json();
}

export async function fetchFeatures(
  startDate?: string,
  endDate?: string
): Promise<{ features: FeatureMetric[]; summary: Summary }> {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const url = `${API_BASE_URL}/api/features${params.toString() ? `?${params.toString()}` : ''}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error('Failed to fetch features');
  }
  
  return response.json();
}

export async function fetchTimeseries(
  startDate?: string,
  endDate?: string
): Promise<{ timeseries: TimeSeriesData[] }> {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const url = `${API_BASE_URL}/api/timeseries${params.toString() ? `?${params.toString()}` : ''}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error('Failed to fetch timeseries');
  }
  
  return response.json();
}
