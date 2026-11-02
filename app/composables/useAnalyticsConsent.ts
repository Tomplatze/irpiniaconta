type AnalyticsChoice = 'accepted' | 'rejected';

interface StoredChoice {
  version: 1;
  choice: AnalyticsChoice;
  expiresAt: number;
}

const storageKey = 'irpiniaconta-analytics-consent';

/** Manage the visitor's analytics choice without loading Google before consent. */
export function useAnalyticsConsent() {
  const config = useRuntimeConfig();
  const route = useRoute();
  const nuxtApp = useNuxtApp();
  const measurementId = config.public.analyticsId;
  const available = computed(() => config.public.analyticsPolicyReady === true && /^G-[A-Z0-9]+$/.test(measurementId));
  const preview = computed(() => import.meta.dev && route.query.anteprimaCookie === '1');
  const choice = useState<AnalyticsChoice | null>('analytics-choice', () => null);
  const visible = useState('analytics-banner-visible', () => false);
  const storageError = useState('analytics-storage-error', () => false);
  const { initialize, disableAnalytics, enableAnalytics } = useGtag();

  function enable() {
    enableAnalytics(measurementId);
    nuxtApp.runWithContext(() => initialize(measurementId));
  }

  function readChoice(): AnalyticsChoice | null {
    try {
      const raw = localStorage.getItem(storageKey);
      if (!raw) return null;
      const value: unknown = JSON.parse(raw);
      if (typeof value !== 'object' || value === null) return null;
      const saved = value as Partial<StoredChoice>;
      if (saved.version !== 1 || (saved.choice !== 'accepted' && saved.choice !== 'rejected') || typeof saved.expiresAt !== 'number' || !Number.isFinite(saved.expiresAt) || saved.expiresAt <= Date.now()) return null;
      return saved.choice;
    } catch {
      return null;
    }
  }

  function start() {
    if (preview.value) { visible.value = true; return; }
    if (!available.value) return;
    choice.value = readChoice();
    visible.value = choice.value === null;
    if (choice.value === 'accepted') enable();
    else removeAnalyticsCookies();
  }

  function removeAnalyticsCookies() {
    const domains = location.hostname.split('.');
    const cookieDomains = ['', ...domains.map((_, index) => domains.slice(index).join('.'))];
    for (const cookie of document.cookie.split(';')) {
      const name = cookie.trim().split('=')[0];
      if (!name || !/^_ga(?:_|$)/.test(name)) continue;
      for (const domain of cookieDomains) {
        document.cookie = `${name}=; Max-Age=0; Path=/; SameSite=Lax${domain ? `; Domain=${domain}` : ''}`;
      }
    }
  }

  function choose(next: AnalyticsChoice) {
    if (preview.value || !available.value) { visible.value = false; return; }
    storageError.value = false;
    const expiresAt = new Date();
    expiresAt.setMonth(expiresAt.getMonth() + 6);
    try {
      localStorage.setItem(storageKey, JSON.stringify({ version: 1, choice: next, expiresAt: expiresAt.getTime() } satisfies StoredChoice));
    } catch {
      // Without persistent storage, do not enable analytics.
      if (next === 'accepted') {
        storageError.value = true;
        return;
      }
      try { localStorage.removeItem(storageKey); } catch { storageError.value = true; }
    }
    const previouslyAccepted = choice.value === 'accepted';
    choice.value = next;
    visible.value = storageError.value;
    if (next === 'accepted' && !previouslyAccepted) enable();
    if (next === 'rejected') {
      disableAnalytics(measurementId);
      removeAnalyticsCookies();
      if (previouslyAccepted && !storageError.value) location.reload();
    }
  }

  function openPreferences() {
    visible.value = true;
  }

  return { available, preview, choice, visible, storageError, start, choose, openPreferences };
}
