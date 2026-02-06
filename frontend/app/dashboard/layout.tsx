'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { Loader2 } from 'lucide-react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    // Only redirect after loading is complete AND we confirmed no user
    if (!isLoading && !user) {
      console.log('Dashboard: No user, redirecting to login');
      router.push('/login');
    } else if (!isLoading && user) {
      console.log('Dashboard: User authenticated:', user.email);
    }
  }, [user, isLoading, router]);

  // Always show loading while checking auth
  if (isLoading) {
    console.log('Dashboard: Loading auth state...');
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // Don't render anything if no user (will redirect)
  if (!user) {
    console.log('Dashboard: No user, returning null');
    return null;
  }

  console.log('Dashboard: Rendering children for user:', user.email);
  return <>{children}</>;
}
