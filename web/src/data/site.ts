/**
 * Datos de la web de Combata.
 *
 * REGLA: aquí solo van datos confirmados. Lo que está pendiente se deja en `null`
 * o con `pendiente: true`, y la interfaz lo muestra como «por confirmar».
 * Ver sección 15 del documento maestro (decisiones abiertas).
 */

/** Muestra etiquetas «Pendiente» en la web mientras se completa la información. */
export const SHOW_PENDING = false;

/** Mientras sea true, la web pide a los buscadores que no la indexen (pre-lanzamiento). */
export const PRELAUNCH = true;

export const site = {
  name: 'Combata',
  tagline: 'Ponle un Combata.',
  /** TODO: correo, teléfono y dirección reales. */
  contact: {
    email: null as string | null,
    phone: null as string | null,
  },
  /** TODO: perfiles reales de redes sociales. Ej.: { label: 'Instagram', href: 'https://…' } */
  social: [] as { label: string; href: string }[],
  /** Endpoint del formulario Custom (variable de entorno PUBLIC_QUOTE_ENDPOINT). */
  quoteEndpoint: (import.meta.env.PUBLIC_QUOTE_ENDPOINT as string | undefined) || null,
};

export type Colour = {
  id: string;
  name: string;
  hex: string;
  available: boolean;
  /** true = color no confirmado todavía por producción/stock. */
  pendiente: boolean;
};

export type Pack = { id: string; label: string; units: number; price: number; discount: string | null };

export const product = {
  id: 'combata-original',
  name: 'Combata Original',
  href: '/productos/combata-original',
  short: 'La tapa reutilizable que se adapta a tu vaso.',
  /**
   * Precio (IVA incluido) según el diseño de la web. Confirmar antes del lanzamiento.
   */
  price: 3.99 as number | null,
  /**
   * Colores según el diseño de la web. Confirmar stock antes del lanzamiento.
   */
  colours: [
    { id: 'lima', name: 'Lima', hex: '#D9FF00', available: true, pendiente: false },
    { id: 'rosa', name: 'Rosa', hex: '#FF4FA0', available: true, pendiente: false },
    { id: 'lavanda', name: 'Lavanda', hex: '#C3A9F5', available: true, pendiente: false },
    { id: 'crema', name: 'Crema', hex: '#F3EEE8', available: true, pendiente: false },
  ] as Colour[],
  /** Packs según el diseño. Confirmar precios antes del lanzamiento. Vacío = sin selector. */
  packs: [
    { id: 'unidad', label: '1 unidad', units: 1, price: 3.99, discount: null },
    { id: 'pack-3', label: 'Pack 3', units: 3, price: 10.99, discount: '-8%' },
    { id: 'pack-5', label: 'Pack 5', units: 5, price: 17.99, discount: '-10%' },
  ] as Pack[],
  /**
   * Valoraciones: SOLO reseñas reales verificadas (p. ej. { rating: 4.8, count: 326 }).
   * Mientras sea null no se muestran estrellas.
   */
  reviews: null as { rating: number; count: number } | null,
  /** Datos verificados del producto. Lo que es `null` aparece como «por confirmar». */
  details: {
    material: 'Silicona flexible' as string | null,
    medidas: null as string | null,
    compatibilidad: 'Se adapta a la mayoría de vasos' as string | null,
    cuidados: null as string | null,
    envio: 'Envío en 24–48 h' as string | null,
  },
  maxQty: 20,
};

export const nav = [
  { label: 'Comprar', href: '/comprar' },
  { label: 'Combata Custom', href: '/custom' },
  { label: 'Sobre Combata', href: '/sobre-combata' },
  { label: 'FAQ', href: '/preguntas-frecuentes' },
];

export const legal = [
  { slug: 'aviso-legal', label: 'Aviso legal' },
  { slug: 'privacidad', label: 'Política de privacidad' },
  { slug: 'cookies', label: 'Política de cookies' },
  { slug: 'terminos-de-compra', label: 'Términos de compra' },
  { slug: 'envios-y-devoluciones', label: 'Envíos y devoluciones' },
];

export const formatPrice = (n: number | null) =>
  n == null ? null : new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
