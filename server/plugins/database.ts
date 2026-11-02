import { closeDatabase } from '../utils/database';

/** Close pooled connections during Nitro shutdown. */
export default defineNitroPlugin(nitro => {
  nitro.hooks.hook('close', closeDatabase);
});
