/** Reviewed, aggregate-only health publication stored as a versioned database snapshot. */
export interface HealthPublication {
  version: 1;
  sources: { id: string; title: string; publisher: string; url: string; period: string; rights: string }[];
  series: Record<string, Record<string, { year: number; value: number }[]>>;
  causes: { code: string; name: string; points: { year: number; value: number }[] }[];
  cancer: { label: string; entries: { name: string; value: number; low: number; high: number }[] }[];
  autism: { value: number; source: string; period: string };
  survey: { value: number; low: number; high: number; source: string; period: string };
  beds: { total: number; year: number; source: string; byType: HealthNamedValue[]; byRegime: HealthNamedValue[]; byProvider: HealthNamedValue[] };
  admissions: { total: number; year: number; source: string };
  staff: { total: number; year: number; source: string; physicians: number; nurses: number; roles: HealthNamedValue[] };
}

/** One named aggregate in a published breakdown. */
export interface HealthNamedValue { name: string; value: number }
