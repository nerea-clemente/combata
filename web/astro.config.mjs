// @ts-check
import { defineConfig } from 'astro/config';

// TODO: definir el dominio definitivo (necesario para URLs canónicas y sitemap).
export default defineConfig({
  site: process.env.SITE_URL || undefined,
  // En GitHub Pages la web vive en /combata (lo pone el workflow con BASE_PATH).
  base: process.env.BASE_PATH || '/',
  trailingSlash: 'never',
  build: { format: 'file' },
});
