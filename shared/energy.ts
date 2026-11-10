export interface EnergyYear {
  year: number;
  generation?: { gross: number; auxiliaries: number; net: number };
  production: Record<'hydro' | 'geothermal' | 'solar' | 'wind' | 'bioenergy', number | null> & { total: number };
  consumption: Record<'agriculture' | 'industry' | 'services' | 'domestic' | 'total', number>;
  source: { url: string; generationPage?: number; productionPage: number; consumptionPage: number; sha256: string };
}

export interface EnergyPublication {
  version: 1;
  scope: '064';
  unit: 'GWh';
  years: EnergyYear[];
  rightsUrl: string;
}
