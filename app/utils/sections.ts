/** Display only source-defined periods; school years remain academic years. */
export function sectionPeriod(period: string, metricId?: string): string {
  if (period === 'undated') return 'Rilevazione non datata dalla fonte';
  if (period === 'mixed_vintages') return 'Anno della cartografia non specificato';
  if (metricId === 'state_school_sites' && /^\d{4}$/.test(period)) return `${period}/${Number(period)+1} · anno scolastico`;
  if (/^\d{4}-\d{2}$/.test(period)) return new Intl.DateTimeFormat('it-IT',{month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(`${period}-01T12:00:00Z`));
  if (/^\d{4}-\d{2}-\d{2}$/.test(period)) return new Intl.DateTimeFormat('it-IT',{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(`${period}T12:00:00Z`));
  return period;
}
