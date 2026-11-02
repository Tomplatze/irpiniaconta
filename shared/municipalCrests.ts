export interface MunicipalCrest {
  code: string;
  name: string;
  page?: string;
  image?: string;
  file?: string;
  kind?: 'official' | 'redrawn';
  artist?: string;
  error?: string;
}

export interface MunicipalCrestManifest {
  source: string;
  license: string;
  license_url: string;
  records: MunicipalCrest[];
}
