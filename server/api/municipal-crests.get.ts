import { readCrestManifest } from '../utils/municipal-crests';

/** Expose attribution and available images without internal file details. */
export default defineEventHandler(async () => {
  const manifest = await readCrestManifest();
  return {
    source: manifest?.source ?? 'https://www.araldicacivica.it/comuni/',
    license: manifest?.license ?? 'CC BY-NC-ND 3.0',
    license_url: manifest?.license_url ?? 'https://creativecommons.org/licenses/by-nc-nd/3.0/',
    records: (manifest?.records ?? []).map(({ code, name, page, file, kind, artist }) => ({ code, name, page, file, kind, artist })),
  };
});
