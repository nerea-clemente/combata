/**
 * Preguntas frecuentes. `answer: null` = respuesta pendiente de validar con
 * información técnica o comercial real (no se inventa).
 */
export type Faq = { q: string; answer: string | null; group: 'producto' | 'compra' | 'custom' };

export const faqs: Faq[] = [
  {
    group: 'producto',
    q: '¿Qué es Combata?',
    answer:
      'Un protector flexible de silicona que se coloca sobre el vaso. Añade una barrera física adicional y ayuda a reducir salpicaduras. Está pensado para fiestas, festivales, celebraciones y otros planes.',
  },
  { group: 'producto', q: '¿Cómo se coloca?', answer: null },
  { group: 'producto', q: '¿Con qué tipos y tamaños de vaso es compatible?', answer: null },
  { group: 'producto', q: '¿Se puede utilizar con pajita?', answer: null },
  { group: 'producto', q: '¿De qué material está hecho?', answer: 'De silicona flexible. Estamos preparando la ficha técnica completa del material.' },
  { group: 'producto', q: '¿Cómo se limpia?', answer: null },
  {
    group: 'producto',
    q: '¿Se puede reutilizar?',
    answer: 'Sí, Combata está pensado para reutilizarse. Las instrucciones de limpieza y la vida útil estimada se publicarán con la ficha técnica.',
  },
  { group: 'producto', q: '¿Cuántas veces se puede reutilizar?', answer: null },
  {
    group: 'producto',
    q: '¿Evita que alguien manipule mi bebida?',
    answer:
      'Combata añade una barrera física sobre el vaso, pero no garantiza que una bebida no pueda ser manipulada ni elimina los riesgos. Es un accesorio complementario, no un sistema de seguridad infalible.',
  },
  { group: 'compra', q: '¿Qué colores hay disponibles?', answer: null },
  { group: 'compra', q: '¿Cuánto cuesta el envío y cuánto tarda?', answer: null },
  { group: 'compra', q: '¿Puedo devolverlo?', answer: null },
  {
    group: 'custom',
    q: '¿Cómo personalizo Combata para mi evento?',
    answer:
      'Rellena el formulario de Combata Custom contándonos tu idea, el tipo de evento y la cantidad aproximada. Con esa información preparamos una propuesta y, si te encaja, confirmamos diseño y pedido.',
  },
  { group: 'custom', q: '¿Hay una cantidad mínima para Custom?', answer: null },
  { group: 'custom', q: '¿Cuánto tarda un pedido personalizado?', answer: null },
  { group: 'custom', q: '¿Qué archivos necesito para el diseño?', answer: null },
];

export const PENDING_ANSWER =
  'Estamos preparando esta respuesta con la información técnica y comercial definitiva. Si la necesitas ya, escríbenos.';
