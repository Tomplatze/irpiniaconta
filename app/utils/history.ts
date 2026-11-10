import type { ValueStatus } from '../../shared/types';

/** Source periods are actual dates or calendar years; never space unequal years as equal time. */
export function periodTimestamp(period: string): number {
  return Date.parse(/^\d{4}$/.test(period) ? `${period}-01-01T00:00:00Z` : `${/^\d{4}-\d{2}$/.test(period) ? period+'-01' : period}T00:00:00Z`);
}

export interface HistoryValue { period: string; value: number | null; status: ValueStatus }
export interface PlotPoint { x: number; y: number; period: string; value: number }
export interface HistoryPlot { path: string; areaPaths: string[]; points: PlotPoint[] }

/** Preserve gaps and negative values; missing/suppressed values never become zero or connected lines. */
export function buildHistoryPlot(values: HistoryValue[]): HistoryPlot {
  const rows = values.map((row) => ({ ...row, time: periodTimestamp(row.period) })).filter((row) => Number.isFinite(row.time)).sort((left, right) => left.time - right.time);
  const measured = rows.filter((row) => row.status === 'observed' && row.value !== null && Number.isFinite(row.value));
  if (!measured.length) return { path: '', areaPaths: [], points: [] };
  const min = Math.min(...measured.map((row) => row.value!));
  const max = Math.max(...measured.map((row) => row.value!));
  const start = rows[0]!.time; const duration = rows[rows.length - 1]!.time - start;
  const points: PlotPoint[] = []; const commands: string[] = []; const segments: PlotPoint[][] = [];
  let connect = false;
  for (const row of rows) {
    if (row.status !== 'observed' || row.value === null || !Number.isFinite(row.value)) { connect = false; continue; }
    const x = duration ? 24 + ((row.time - start) / duration) * 552 : 300;
    const y = max === min ? 90 : 156 - ((row.value - min) / (max - min)) * 132;
    const point = { x, y, period: row.period, value: row.value };
    commands.push(`${connect ? 'L' : 'M'}${x.toFixed(2)},${y.toFixed(2)}`);
    if (!connect) segments.push([]);
    segments.at(-1)!.push(point);
    points.push(point); connect = true;
  }
  const areaPaths = segments.filter(segment => segment.length > 1).map(segment => {
    const first = segment[0]!; const last = segment.at(-1)!;
    return `M${first.x.toFixed(2)},174 ${segment.map(point => `L${point.x.toFixed(2)},${point.y.toFixed(2)}`).join(' ')} L${last.x.toFixed(2)},174 Z`;
  });
  return { path: commands.join(' '), areaPaths, points };
}

export interface OverlayInput { code: string; name: string; values: Array<HistoryValue & { detail?: string }> }
export interface OverlayPlot {
  minimum: number; maximum: number; ticks: number[]; periods: Array<{ period: string; x: number }>;
  zeroY: number; barWidth: number;
  series: Array<{ code: string; name: string; path: string; areaPaths: string[]; points: PlotPoint[] }>;
}

/** Project every municipality onto one time/value domain; union periods expose missing gaps. */
export function buildOverlayPlot(series: OverlayInput[], width = 720, options: { includeZero?: boolean; bars?: boolean; percentChange?: boolean } = {}): OverlayPlot {
  const periods = [...new Set(series.flatMap(item => item.values.map(point => point.period)))].filter(period => Number.isFinite(periodTimestamp(period))).sort((a,b) => periodTimestamp(a)-periodTimestamp(b));
  const values = series.flatMap(item => item.values.filter(point => point.status === 'observed' && point.value !== null && Number.isFinite(point.value) && periods.includes(point.period)).map(point => point.value!));
  const minimum = values.length ? Math.min(...values) : 0; const maximum = values.length ? Math.max(...values) : 0;
  const padding = maximum === minimum ? Math.max(Math.abs(maximum)*.05, 1) : (maximum-minimum)*.12;
  let low = options.includeZero && minimum >= 0 ? 0 : minimum-padding;
  let high = options.includeZero && maximum <= 0 && minimum < 0 ? 0 : maximum+padding;
  if (options.percentChange) {
    // Keep a symmetric reference where possible. Nonnegative measurements can fall at most 100%.
    const extent = Math.max(1, -minimum, maximum);
    const step = 2 * 10 ** Math.floor(Math.log10(extent));
    high = Math.ceil(extent / step) * step;
    low = -Math.min(high, 100);
  }
  const start = periodTimestamp(periods[0] ?? '2000'); const duration = periodTimestamp(periods.at(-1) ?? '2000')-start;
  const plotWidth = width-86;
  const intervalRatios = periods.slice(1).map((period,index)=>(periodTimestamp(period)-periodTimestamp(periods[index]!))/duration);
  const shortestRatio = intervalRatios.length ? Math.min(...intervalRatios) : 1;
  const barWidth = Math.max(1,Math.min(34,options.bars ? .62*shortestRatio*(plotWidth-8)/(1+.62*shortestRatio) : .62*shortestRatio*plotWidth));
  // Reserve each edge's half-column plus a gap while retaining a linear calendar domain.
  const inset = options.bars ? barWidth/2+4 : 0;
  const x = (period: string): number => duration ? 54+inset+(periodTimestamp(period)-start)/duration*(plotWidth-2*inset) : (width+22)/2;
  const y = (value: number): number => 208-(value-low)/(high-low)*180;
  const zeroY = y(0);
  const coordinates = periods.map(period => ({ period, x: x(period) }));
  const ticks = options.includeZero && low<0 && high>0 ? [high,0,low].filter(value=>value===0 || Math.abs(y(value)-zeroY)>22) : [high,(high+low)/2,low];
  return { minimum: low, maximum: high, zeroY, barWidth, ticks, periods: coordinates,
    series: series.map(item => {
      const rows = new Map(item.values.map(point => [point.period,point]));
      const points: PlotPoint[] = []; const commands: string[] = []; const segments: PlotPoint[][] = []; let connect = false;
      for (const period of periods) {
        const row = rows.get(period);
        if (!row || row.status !== 'observed' || row.value === null || !Number.isFinite(row.value)) { connect = false; continue; }
        const point = { period, value: row.value, x: x(period), y: y(row.value) };
        commands.push(`${connect ? 'L' : 'M'}${point.x.toFixed(2)},${point.y.toFixed(2)}`);
        if (!connect) segments.push([]);
        segments.at(-1)!.push(point);
        points.push(point); connect = true;
      }
      const areaBaseline = options.includeZero ? zeroY : 208;
      const areaPaths = segments.filter(segment => segment.length > 1).map(segment => {
        const first = segment[0]!; const last = segment.at(-1)!;
        return `M${first.x.toFixed(2)},${areaBaseline.toFixed(2)} ${segment.map(point => `L${point.x.toFixed(2)},${point.y.toFixed(2)}`).join(' ')} L${last.x.toFixed(2)},${areaBaseline.toFixed(2)} Z`;
      });
      return { code: item.code, name: item.name, points, path: commands.join(' '), areaPaths };
    }) };
}

export interface MonthlyCell extends HistoryValue { label: string; fraction: number | null }
export interface MonthlyCalendar { year: string | null; minimum: number | null; maximum: number | null; cells: MonthlyCell[] }

/** Keep one source year on a complete calendar; absent, suppressed and missing months stay empty. */
export function buildMonthlyCalendar(values: HistoryValue[]): MonthlyCalendar {
  const valid = values.filter(point => /^\d{4}-(0[1-9]|1[0-2])$/.test(point.period));
  const year = valid.map(point => point.period.slice(0,4)).sort().at(-1) ?? null;
  if (!year) return { year: null, minimum: null, maximum: null, cells: [] };
  const records = new Map(valid.filter(point => point.period.startsWith(year)).map(point => [point.period,point]));
  const measured = [...records.values()].filter(point => point.status==='observed' && point.value!==null && Number.isFinite(point.value)).map(point => point.value!);
  const minimum = measured.length ? Math.min(...measured) : null;
  const maximum = measured.length ? Math.max(...measured) : null;
  const cells = Array.from({length:12},(_,index): MonthlyCell => {
    const period = `${year}-${String(index+1).padStart(2,'0')}`;
    const row = records.get(period);
    const observed = row?.status==='observed' && row.value!==null && Number.isFinite(row.value);
    return { period, value: observed ? row.value : null, status: row?.status ?? 'missing',
      label: new Intl.DateTimeFormat('it-IT',{month:'short',timeZone:'UTC'}).format(new Date(`${period}-01T00:00:00Z`)).replace('.',''),
      fraction: observed && minimum!==null && maximum!==null ? maximum===minimum ? .5 : (row.value!-minimum)/(maximum-minimum) : null };
  });
  return { year, minimum, maximum, cells };
}
