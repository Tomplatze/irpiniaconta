/** Public downloads are retired; original evidence remains stored for audit and recovery. */
export default defineEventHandler(() => {
  throw createError({
    statusCode: 410,
    statusMessage: 'Data downloads are not available. Consult the official sources.',
    data: { sourceCatalogue: '/raccolta' },
  });
});
