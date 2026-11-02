import type { DemographicFlow, DemographicFlowPoint } from '../../shared/demographicFlows';
import type { SectionPoint } from '../../shared/sections';

export interface FlowCoordinate { period: string; x: number; y: number; value: number }
export interface FlowComponentPlot {
  id: 'positive' | 'negative';
  path: string;
  areaPaths: string[];
  points: FlowCoordinate[];
}
export interface DemographicFlowPlot {
  width: number;
  height: number;
  left: number;
  right: number;
  top: number;
  bottom: number;
  zeroY: number;
  maximum: number;
  barWidth: number;
  hasData: boolean;
  periods: Array<{ period: string; x: number }>;
  ticks: Array<{ value: number; y: number }>;
  components: FlowComponentPlot[];
}

/** Event magnitudes stay non-negative; lower bars are an orientation, never negative deaths. */
export function observedFlowCount(point: SectionPoint | undefined): number | null {
  return point?.status === 'observed' && point.value !== null && Number.isFinite(point.value) && point.value >= 0 ? point.value : null;
}

/** Translate the known source flag without assuming any particular year is provisional. */
export function demographicFlowPeriodNote(value: string | undefined): string {
  if (!value) return '';
  const note = value.trim();
  if (/^Provisional \(p\)$/i.test(note)) return 'Dato provvisorio indicato dalla fonte (p).';
  if (/^See source information flag and release notes$/i.test(note)) return 'Per questo periodo, la fonte rimanda alle proprie note di rilascio.';
  return value;
}

/** Annual flow observations use real calendar positions, including leap-year distances. */
function timestamp(period: string): number {
  return /^\d{4}$/.test(period) ? Date.parse(`${period}-01-01T00:00:00Z`) : Number.NaN;
}

/** Keep count axes legible and integer-valued, including small and all-zero populations. */
function countCeiling(value: number): number {
  if (value <= 1) return 1;
  const magnitude = 10 ** Math.floor(Math.log10(value));
  const fraction = value / magnitude;
  const step = fraction <= 1 ? 1 : fraction <= 2 ? 2 : fraction <= 2.5 ? 2.5 : fraction <= 4 ? 4 : fraction <= 5 ? 5 : fraction <= 6 ? 6 : fraction <= 8 ? 8 : 10;
  return Math.ceil(step * magnitude);
}

/** Project a single territory's paired annual counts onto a shared scale and calendar. */
export function buildDemographicFlowPlot(flow: DemographicFlow, availableWidth = 720): DemographicFlowPlot {
  const width = Math.max(240, Number.isFinite(availableWidth) ? availableWidth : 720);
  const left = 48; const right = width - 20; const top = 28; const bottom = 244;
  const natural = flow.kind === 'natural';
  const rows = flow.series.length === 1 ? flow.series[0]!.values.filter(row => Number.isFinite(timestamp(row.period))).toSorted((a,b) => timestamp(a.period) - timestamp(b.period)) : [];
  const periods = [...new Set(rows.map(row => row.period))];
  const records = new Map<string, DemographicFlowPoint>(rows.map(row => [row.period,row]));
  const counts = rows.flatMap(row => [observedFlowCount(row.positive), observedFlowCount(row.negative)]).filter((value): value is number => value !== null);
  const maximum = countCeiling(counts.length ? Math.max(...counts) : 0);
  const zeroY = natural ? (top + bottom) / 2 : bottom;
  const magnitudeHeight = natural ? (bottom - top) / 2 : bottom - top;
  const y = (value: number, direction: number): number => zeroY - direction * value / maximum * magnitudeHeight;
  const start = timestamp(periods[0] ?? '2000'); const duration = timestamp(periods.at(-1) ?? '2000') - start;
  const intervalRatios = periods.slice(1).map((period,index) => (timestamp(period) - timestamp(periods[index]!)) / duration);
  const shortestRatio = intervalRatios.length ? Math.min(...intervalRatios) : 1;
  const plotWidth = right - left;
  const barWidth = Math.max(1, Math.min(32, .62 * shortestRatio * (plotWidth - 8) / (1 + .62 * shortestRatio)));
  const inset = natural ? barWidth / 2 + 4 : 0;
  const x = (period: string): number => duration ? left + inset + (timestamp(period) - start) / duration * (plotWidth - 2 * inset) : (left + right) / 2;
  const coordinates = periods.map(period => ({ period, x: x(period) }));
  const half = maximum / 2;
  const magnitudes = Number.isInteger(half) && maximum > 1 ? [0,half,maximum] : [0,maximum];
  const signedTicks = natural ? [...magnitudes.toReversed().filter(value => value > 0),0,...magnitudes.filter(value => value > 0).map(value => -value)] : magnitudes.toReversed();
  const components = (['positive','negative'] as const).map((id): FlowComponentPlot => {
    const points: FlowCoordinate[] = []; const commands: string[] = []; const segments: FlowCoordinate[][] = []; let connect = false;
    const direction = natural && id === 'negative' ? -1 : 1;
    for (const period of periods) {
      const count = observedFlowCount(records.get(period)?.[id]);
      if (count === null) { connect = false; continue; }
      const point = {period, value: count, x: x(period), y: y(count,direction)};
      commands.push(`${connect ? 'L' : 'M'}${point.x.toFixed(2)},${point.y.toFixed(2)}`);
      if (!connect) segments.push([]);
      segments.at(-1)!.push(point);
      points.push(point); connect = true;
    }
    const areaPaths = segments.filter(segment => segment.length > 1).map(segment => {
      const first = segment[0]!; const last = segment.at(-1)!;
      return `M${first.x.toFixed(2)},${bottom.toFixed(2)} ${segment.map(point => `L${point.x.toFixed(2)},${point.y.toFixed(2)}`).join(' ')} L${last.x.toFixed(2)},${bottom.toFixed(2)} Z`;
    });
    return {id,points,path:commands.join(' '),areaPaths};
  });
  return {width,height:292,left,right,top,bottom,zeroY,maximum,barWidth,hasData:counts.length>0,periods:coordinates,
    ticks:signedTicks.map(value => ({value:Math.abs(value),y:y(Math.abs(value),value<0 ? -1 : 1)})),components};
}
