/**
 * Carrito local (localStorage). Funciona de verdad para añadir, cambiar y quitar
 * productos. NO hay checkout: la plataforma de ecommerce y la pasarela de pago
 * están pendientes (sección 14 del documento maestro). Cuando se elija
 * (p. ej. Shopify), sustituir `checkoutAvailable` y `goToCheckout`.
 */
import { product, formatPrice } from '../data/site';

export type CartLine = { productId: string; colourId: string | null; packId: string | null; qty: number };

const KEY = 'combata-cart-v1';
export const checkoutAvailable = false;

const read = (): CartLine[] => {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || '[]');
    return Array.isArray(raw) ? raw.filter((l) => l && typeof l.qty === 'number' && l.qty > 0) : [];
  } catch {
    return [];
  }
};
const write = (lines: CartLine[]) => {
  localStorage.setItem(KEY, JSON.stringify(lines));
  document.dispatchEvent(new CustomEvent('cart:change', { detail: lines }));
};

export const getLines = read;
export const count = () => read().reduce((n, l) => n + l.qty, 0);
const same = (a: CartLine, b: Omit<CartLine, 'qty'>) =>
  a.productId === b.productId && a.colourId === b.colourId && a.packId === b.packId;

export function addLine(line: CartLine) {
  if (line.productId !== product.id) throw new Error('Producto desconocido');
  if (line.colourId) {
    const c = product.colours.find((c) => c.id === line.colourId);
    if (!c || !c.available) throw new Error('Este color no está disponible');
  }
  const lines = read();
  const found = lines.find((l) => same(l, line));
  if (found) found.qty = Math.min(product.maxQty, found.qty + line.qty);
  else lines.push({ ...line, qty: Math.min(product.maxQty, line.qty) });
  write(lines);
}
export function setQty(index: number, qty: number) {
  const lines = read();
  if (!lines[index]) return;
  if (qty <= 0) lines.splice(index, 1);
  else lines[index].qty = Math.min(product.maxQty, qty);
  write(lines);
}
export const removeLine = (index: number) => setQty(index, 0);

export function describe(line: CartLine) {
  const colour = product.colours.find((c) => c.id === line.colourId) || null;
  const pack = product.packs.find((p) => p.id === line.packId) || null;
  const unit = pack ? pack.price : product.price;
  return {
    name: product.name,
    colour,
    pack,
    unitLabel: formatPrice(unit),
    totalLabel: unit == null ? null : formatPrice(unit * line.qty),
    total: unit == null ? null : unit * line.qty,
  };
}
export function subtotalLabel() {
  const lines = read();
  if (!lines.length) return formatPrice(0);
  let sum = 0;
  for (const l of lines) {
    const d = describe(l);
    if (d.total == null) return null;
    sum += d.total;
  }
  return formatPrice(sum);
}

const esc = (s: string) => s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]!);

/** Pinta las líneas del carrito dentro de un contenedor (drawer y página /carrito). */
export function renderLines(el: HTMLElement) {
  const lines = read();
  if (!lines.length) {
    el.innerHTML = `<div class="cart-empty"><p class="h-3">Tu carrito está vacío.</p><p class="muted">Cuando añadas tu Combata, aparecerá aquí.</p><a class="btn btn-primary" href="${product.href}">Ver Combata Original</a></div>`;
    return;
  }
  el.innerHTML = `<ul class="cart-lines" role="list">${lines
    .map((l, i) => {
      const d = describe(l);
      const swatch = d.colour ? `<span class="cart-swatch" style="background:${d.colour.hex}" aria-hidden="true"></span>` : '';
      const meta = [d.colour ? `Color: ${esc(d.colour.name)}` : null, d.pack ? esc(d.pack.label) : null].filter(Boolean).join(' · ');
      return `<li class="cart-line">
        <div class="cart-line__thumb">${swatch}</div>
        <div class="cart-line__body">
          <p class="cart-line__name">${esc(d.name)}</p>
          ${meta ? `<p class="cart-line__meta">${meta}</p>` : ''}
          <div class="qty qty--s" role="group" aria-label="Cantidad de ${esc(d.name)}">
            <button type="button" data-qty="${i}" data-delta="-1" aria-label="Quitar una unidad">−</button>
            <output aria-live="polite">${l.qty}</output>
            <button type="button" data-qty="${i}" data-delta="1" aria-label="Añadir una unidad" ${l.qty >= product.maxQty ? 'disabled' : ''}>+</button>
          </div>
        </div>
        <div class="cart-line__side">
          <p class="cart-line__price">${d.totalLabel ?? '<span class="pending">Precio por confirmar</span>'}</p>
          <button type="button" class="cart-line__remove" data-remove="${i}">Eliminar</button>
        </div>
      </li>`;
    })
    .join('')}</ul>`;
}

/** Delegación de eventos para + / − / eliminar. */
export function bindLineControls(el: HTMLElement, announce?: (msg: string) => void) {
  el.addEventListener('click', (e) => {
    const t = (e.target as HTMLElement).closest('button');
    if (!t) return;
    const lines = read();
    if (t.dataset.remove != null) {
      setQty(Number(t.dataset.remove), 0);
      announce?.('Producto eliminado del carrito');
    } else if (t.dataset.qty != null) {
      const i = Number(t.dataset.qty);
      setQty(i, (lines[i]?.qty || 0) + Number(t.dataset.delta));
    }
  });
}

export function toast(message: string, kind: 'ok' | 'error' = 'ok') {
  const region = document.querySelector<HTMLElement>('[data-toast]');
  if (!region) return;
  const item = document.createElement('div');
  item.className = `toast toast--${kind}`;
  item.setAttribute('role', kind === 'error' ? 'alert' : 'status');
  item.textContent = message;
  region.appendChild(item);
  setTimeout(() => item.classList.add('is-out'), 3200);
  setTimeout(() => item.remove(), 3700);
}
