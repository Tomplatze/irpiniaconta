import { readFile, lstat } from 'node:fs/promises';
import { join } from 'node:path';
import { crestDirectory, readCrestManifest } from '../../utils/municipal-crests';

const mimeTypes: Record<string, string> = { jpg: 'image/jpeg', png: 'image/png', gif: 'image/gif', webp: 'image/webp' };

/** Serve only the original image associated with a validated municipal code. */
export default defineEventHandler(async event => {
  const code = getRouterParam(event, 'code') ?? '';
  if (!/^064\d{3}$/.test(code)) throw createError({ statusCode: 404, statusMessage: 'Not Found' });
  const record = (await readCrestManifest())?.records.find(item => item.code === code);
  const match = record?.filename?.match(new RegExp(`^${code}\\.(jpg|png|gif|webp)$`));
  if (!match) throw createError({ statusCode: 404, statusMessage: 'Not Found' });
  const path = join(crestDirectory, record!.filename!);
  try {
    const info = await lstat(path);
    if (!info.isFile() || info.isSymbolicLink()) throw createError({ statusCode: 404, statusMessage: 'Not Found' });
    const image = await readFile(path);
    setHeader(event, 'Content-Type', mimeTypes[match[1]!]!);
    setHeader(event, 'Cache-Control', 'public, max-age=86400');
    setHeader(event, 'X-Content-Type-Options', 'nosniff');
    return image;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') throw createError({ statusCode: 404, statusMessage: 'Not Found' });
    throw error;
  }
});
