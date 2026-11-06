# Web de Combata

Sitio estático hecho con [Astro](https://astro.build). Fuente de verdad: `COMBATA_MASTER_BRIEF_CLAUDE_CODE.md`.

## Arrancar

```bash
npm install
npm run dev       # desarrollo en http://localhost:4321
npm run build     # genera dist/ (HTML estático, se puede alojar en cualquier hosting)
```

Variables de entorno: copia `.env.example` a `.env`.

## Estructura

- `src/data/site.ts`: **datos del producto y de la marca** (precio, colores, packs, contacto, redes). Solo datos confirmados; lo pendiente va en `null`.
- `src/data/faq.ts`: preguntas frecuentes (`answer: null` = respuesta pendiente).
- `src/pages/`: inicio, comprar, ficha de producto, carrito, Custom (+ confirmación), Sobre Combata, FAQ, contacto, legales y 404.
- `src/components/`: Header, Footer, CartDrawer, QuoteForm, FaqList, Placeholder, Pending…
- `src/scripts/cart.ts`: carrito local (localStorage).
- `public/brand/`: recursos de marca reales (logo con ™, nube, stickers) del kit `marca/`.

## Modo pre-lanzamiento

En `src/data/site.ts`:
- `SHOW_PENDING = true` muestra etiquetas «Pendiente» sobre lo que falta por confirmar. Ponlo en `false` al publicar.
- `PRELAUNCH = true` añade `noindex` para que los buscadores no indexen la web. Ponlo en `false` al publicar.

## Qué falta para publicar

| Pendiente | Dónde se configura |
|---|---|
| Fotos reales del producto (principal, colores, material, colocación) y demostración de uso | sustituir los `<Placeholder>` |
| Precio definitivo (3,99 € no aprobado) | `product.price` |
| Colores reales y stock | `product.colours` (`pendiente`, `available`) |
| Packs y precios | `product.packs` (el selector aparece solo si hay packs) |
| Medidas, compatibilidad, cuidados, envío | `product.details` |
| Plataforma de ecommerce y pago (Shopify no aprobado) | `src/scripts/cart.ts` (`checkoutAvailable`) |
| Destino del formulario Custom | `PUBLIC_QUOTE_ENDPOINT` |
| Email, teléfono y redes | `site.contact`, `site.social` |
| Textos legales (aviso legal, privacidad, cookies, términos, envíos) | `src/pages/legal/[slug].astro` |
| Respuestas de FAQ técnicas y B2B (MOQ, plazos, archivos) | `src/data/faq.ts` |
| Historia de las fundadoras | `src/pages/sobre-combata.astro` |
| Ejemplos reales de Custom | `src/pages/custom/index.astro` |
| Dominio | `SITE_URL` |
| Vectorización profesional del logo e isotipo | `public/brand/` (los SVG actuales son una vectorización de la lámina) |

No hay analítica ni cookies de terceros, así que no se incluye banner de cookies. Si se añaden, hará falta gestión de consentimiento.
