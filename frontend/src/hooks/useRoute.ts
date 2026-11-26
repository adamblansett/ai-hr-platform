import { useState, useEffect, useCallback } from 'react';

export const ROUTE_TO_PATH: Record<string, string> = {
  dashboard: '/dashboard',
  orgchart: '/org-chart',
  directory: '/directory',
  onboarding: '/onboarding',
  offboarding: '/offboarding',
  leave: '/leave',
  attendance: '/attendance',
  compensation: '/compensation',
  benchmarking: '/benchmarking',
  benefits: '/benefits',
  expenses: '/expenses',
  workforce: '/workforce-planning',
  coaching: '/coaching',
  pulse: '/pulse',
  recognition: '/recognition',
  learning: '/learning',
  performance: '/performance',
  assets: '/assets',
  contractors: '/contractors',
  immigration: '/immigration',
  localization: '/localization',
  safety: '/safety',
  policies: '/policies',
  notifications: '/notifications',
  security: '/security-sso',
  compliance: '/compliance',
  branding: '/branding',
  integrations: '/integrations',
};

const PATH_TO_ROUTE: Record<string, string> = Object.entries(ROUTE_TO_PATH).reduce(
  (acc, [route, path]) => {
    acc[path] = route;
    return acc;
  },
  {} as Record<string, string>
);

function resolveRouteFromLocation(): string {
  const pathname = window.location.pathname.replace(/\/+$/, '') || '/dashboard';
  if (pathname === '' || pathname === '/') {
    return 'dashboard';
  }
  return PATH_TO_ROUTE[pathname] || 'dashboard';
}

export function useRoute() {
  const [activeRoute, setActiveRoute] = useState<string>(() => resolveRouteFromLocation());

  useEffect(() => {
    const onPopState = () => {
      setActiveRoute(resolveRouteFromLocation());
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const navigate = useCallback((route: string) => {
    const targetPath = ROUTE_TO_PATH[route] || '/dashboard';
    if (window.location.pathname !== targetPath) {
      window.history.pushState({ route }, '', targetPath);
    }
    setActiveRoute(route in ROUTE_TO_PATH ? route : 'dashboard');
  }, []);

  return { activeRoute, navigate };
}
