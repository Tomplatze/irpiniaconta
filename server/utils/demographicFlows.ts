import type { PoolClient } from 'pg';
import type { DemographicFlow, DemographicFlowPoint, DemographicFlowSeries } from '../../shared/demographicFlows';
import type { SectionPoint, SectionSource } from '../../shared/sections';
import type { ValueStatus } from '../../shared/types';

export interface FlowScope { code: string | null; name: string }
export interface FlowObservation {
  code: string;
  indicator: string;
  dataset_id: string;
  period: string;
  value: number | null;
  status: ValueStatus;
}

interface FlowDefinition {
  metric: string;
  kind: DemographicFlow['kind'];
  positive: DemographicFlow['positive'];
  negative: DemographicFlow['negative'];
}

interface BalanceMetadata {
  name: string;
  publisher: string;
  landing_url: string;
  license: string | null;
  period_notes?: Record<string, string>;
}

const definitions: FlowDefinition[] = [
  { metric: 'natural_balance', kind: 'natural', positive: { id: 'births', label: 'Nati vivi' }, negative: { id: 'deaths', label: 'Decessi' } },
  { metric: 'foreign_migration_balance', kind: 'foreign', positive: { id: 'foreign_immigrants', label: 'Arrivi dall’estero' }, negative: { id: 'foreign_emigrants', label: 'Partenze per l’estero' } },
];

const observed = (row: FlowObservation | undefined): row is FlowObservation & { value: number } => row?.status === 'observed' && row.value !== null && Number.isFinite(row.value);
const identity = (code: string, indicator: string, period: string): string => `${code}:${indicator}:${period}`;

/** Preserve an original absent/suppressed component rather than manufacturing a zero or net. */
function point(row: FlowObservation | undefined, period: string): SectionPoint {
  return { period, value: row?.value ?? null, status: row?.status ?? 'unavailable', coverage: observed(row) ? 1 : 0 };
}

/** Validate complete same-source pairs and construct chart evidence without changing observations. */
export function buildDemographicFlows(rows: FlowObservation[], scopes: FlowScope[], source: SectionSource, periodNotes: Record<string, string> = {}): Map<string, DemographicFlow> {
  const records = new Map<string, FlowObservation>();
  const knownIndicators = new Set(definitions.flatMap(definition => [definition.metric, definition.positive.id, definition.negative.id]));
  for (const row of rows) {
    if (!knownIndicators.has(row.indicator)) continue;
    if (row.dataset_id !== source.id) throw new Error('Demographic components must use one original source.');
    if (!/^\d{4}$/.test(row.period)) throw new Error('Demographic components require annual source periods.');
    if (row.status === 'observed' ? !observed(row) || !Number.isInteger(row.value) : row.value !== null) throw new Error('Invalid original demographic value state.');
    if (!definitions.some(definition => definition.metric === row.indicator) && observed(row) && row.value < 0) throw new Error('Demographic event counts cannot be negative.');
    const key = identity(row.code, row.indicator, row.period);
    if (records.has(key)) throw new Error('Duplicate demographic observation.');
    records.set(key, row);
  }

  return new Map<string, DemographicFlow>(definitions.map((definition): [string, DemographicFlow] => {
    const identifiers = [definition.positive.id, definition.negative.id, definition.metric];
    const selected = rows.filter(row => identifiers.includes(row.indicator));
    const periods = [...new Set(selected.map(row => row.period))].sort();
    const codes = [...new Set(selected.map(row => row.code))];
    const complete = (code: string, period: string): boolean => identifiers.every(indicator => observed(records.get(identity(code, indicator, period))));

    for (const code of codes) {
      for (const period of periods) {
        if (!complete(code, period)) continue;
        const positive = records.get(identity(code, definition.positive.id, period))!;
        const negative = records.get(identity(code, definition.negative.id, period))!;
        const net = records.get(identity(code, definition.metric, period))!;
        if (positive.value! - negative.value! !== net.value) throw new Error('Original demographic components do not reconcile with their published balance.');
      }
    }

    const cohort = codes.filter(code => periods.every(period => complete(code, period)));
    const valuesFor = (scope: FlowScope): DemographicFlowSeries => {
      const values: DemographicFlowPoint[] = periods.map(period => {
        const component = (indicator: string): SectionPoint => {
          if (scope.code) return point(records.get(identity(scope.code, indicator, period)), period);
          if (!cohort.length) return { period, value: null, status: 'unavailable', coverage: 0 };
          const value = cohort.reduce((sum, code) => sum + records.get(identity(code, indicator, period))!.value!, 0);
          return { period, value, status: 'observed', coverage: cohort.length };
        };
        return { period, positive: component(definition.positive.id), negative: component(definition.negative.id), balance: component(definition.metric) };
      });
      return { ...scope, scope: scope.code ? scope.name : `${cohort.length} comuni con entrambe le componenti e il saldo in tutti i periodi`, values };
    };

    return [definition.metric, { kind: definition.kind, unit: 'persons', positive: definition.positive, negative: definition.negative,
      sources: [source], period_notes: { ...periodNotes }, series: scopes.map(valuesFor) }];
  }));
}

/** Reuse the caller's read-only snapshot; qualified tables keep the sections search path intact. */
export async function getDemographicFlows(database: PoolClient, scopes: FlowScope[]): Promise<Map<string, DemographicFlow>> {
  const dataset = await database.query<{ id: string; verified_at: string; metadata: BalanceMetadata }>('SELECT id,verified_at,metadata FROM atlas.datasets WHERE id=$1 AND status=$2', ['istat_balance', 'ready']);
  const entry = dataset.rows[0];
  if (!entry) return new Map();
  const result = await database.query<FlowObservation>(
    'SELECT o.municipality_code AS code,o.indicator_id AS indicator,i.dataset_id,o.period,o.value,o.status FROM atlas.observations o JOIN atlas.indicators i ON i.id=o.indicator_id WHERE i.dataset_id=$1 AND o.indicator_id=ANY($2::text[]) ORDER BY o.period,o.municipality_code,o.indicator_id',
    [entry.id, definitions.flatMap(definition => [definition.positive.id, definition.negative.id, definition.metric])]);
  const source: SectionSource = { id: entry.id, title: entry.metadata.name, publisher: entry.metadata.publisher,
    url: entry.metadata.landing_url, license: entry.metadata.license, verified_at: entry.verified_at };
  return buildDemographicFlows(result.rows, scopes, source, entry.metadata.period_notes);
}
