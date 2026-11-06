/**
 * Datos de la web de Combata.
 *
 * REGLA: aquí solo van datos confirmados. Lo que está pendiente se deja en `null`
 * o con `pendiente: true`, y la interfaz lo muestra como «por confirmar».
 * Ver sección 15 del documento maestro (decisiones abiertas).
 */

/** Muestra etiquetas «Pendiente» en la web mientras se completa la información. */
export const SHOW_PENDING = true;

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

export type Pack = { id: string; label: string; units: number; price: number };

export const product = {
  id: 'combata-original',
  name: 'Combata Original',
  href: '/productos/combata-original',
  short: 'El protector reutilizable para tu bebida.',
  /**
   * TODO: precio definitivo (IVA incluido). 3,99 € es solo una hipótesis de trabajo,
   * por eso no se publica. Cuando esté aprobado: price: 3.99
   */
  price: null as number | null,
  /**
   * TODO: confirmar los colores reales disponibles y su stock.
   * Los de abajo salen de la paleta de marca y están marcados como pendientes.
   */
  colours: [
    { id: 'lima', name: 'Lima', hex: '#D9FF00', available: true, pendiente: true },
    { id: 'rosa', name: 'Rosa', hex: '#FF2EA6', available: true, pendiente: true },
    { id: 'lavanda', name: 'Lavanda', hex: '#B6A4FF', available: true, pendiente: true },
  ] as Colour[],
  /** TODO: packs reales. Mientras esté vacío, no se muestra el selector de packs. */
  packs: [] as Pack[],
  /** Datos verificados del producto. Lo que es `null` aparece como «por confirmar». */
  details: {
    material: 'Silicona flexible' as string | null,
    medidas: null as string | null,
    compatibilidad: null as string | null,
    cuidados: null as string | null,
    envio: null as string | null,
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
