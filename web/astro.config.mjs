// @ts-check
import { defineConfig } from 'astro/config';

// TODO: definir el dominio definitivo (necesario para URLs canónicas y sitemap).
export default defineConfig({
  site: process.env.SITE_URL || undefined,
  trailingSlash: 'never',
  build: { format: 'file' },
});
