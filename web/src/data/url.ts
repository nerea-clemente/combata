/** Antepone la ruta base del sitio (p. ej. «/combata» en GitHub Pages) a una ruta interna. */
const BASE = (import.meta.env.BASE_URL || '/').replace(/\/$/, '');
export const url = (path: string) => (path.startsWith('/') ? BASE + path : path) || '/';
/** Quita la ruta base de un pathname (para marcar el enlace activo). */
export const stripBase = (pathname: string) =>
  (BASE && pathname.startsWith(BASE) ? pathname.slice(BASE.length) : pathname) || '/';
