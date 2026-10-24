// Dibujo del avatar con SVG.
//
// El avatar es un robot. Un SVG es un dibujo hecho con texto: formas (rectángulos,
// círculos, líneas...) con coordenadas dentro de un lienzo de 200 x 200.
// El orden importa: lo que se escribe después se dibuja ENCIMA de lo anterior.
//
// La base de datos solo guarda el color y el NOMBRE de cada prenda ("capa", "gorra"...);
// los dibujos viven aquí. Para añadir una prenda nueva: agrega su dibujo a ROPAS o ACCESORIOS
// y su fila en backend/app/catalogo_items.py.

const COLOR_POR_DEFECTO = "#58cc02";
const TRAZO = 'stroke="#000" stroke-opacity="0.25" stroke-width="3"';   // contorno suave

// ---------- Ropa ----------
// "atras" se dibuja DETRÁS del cuerpo y "delante" ENCIMA de él.
const ROPAS = {
  camiseta: {
    atras: "",
    delante: `
      <rect x="62" y="124" width="76" height="54" rx="16" fill="#ffffff" ${TRAZO}/>
      <circle cx="100" cy="150" r="9" fill="#1cb0f6"/>
      <rect x="44" y="128" width="14" height="16" rx="7" fill="#ffffff" ${TRAZO}/>
      <rect x="142" y="128" width="14" height="16" rx="7" fill="#ffffff" ${TRAZO}/>`,
  },
  sudadera: {
    atras: "",
    delante: `
      <rect x="62" y="122" width="76" height="58" rx="18" fill="#5b6b8a" ${TRAZO}/>
      <rect x="42" y="126" width="18" height="40" rx="9" fill="#5b6b8a" ${TRAZO}/>
      <rect x="140" y="126" width="18" height="40" rx="9" fill="#5b6b8a" ${TRAZO}/>
      <rect x="78" y="152" width="44" height="18" rx="7" fill="#4a5875"/>
      <line x1="92" y1="126" x2="92" y2="142" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
      <line x1="108" y1="126" x2="108" y2="142" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>`,
  },
  bata: {
    atras: "",
    delante: `
      <rect x="56" y="122" width="88" height="62" rx="12" fill="#ffffff" ${TRAZO}/>
      <rect x="42" y="126" width="18" height="40" rx="9" fill="#ffffff" ${TRAZO}/>
      <rect x="140" y="126" width="18" height="40" rx="9" fill="#ffffff" ${TRAZO}/>
      <polygon points="84,122 100,122 100,152" fill="#dbe8f2"/>
      <polygon points="116,122 100,122 100,152" fill="#dbe8f2"/>
      <line x1="100" y1="152" x2="100" y2="184" stroke="#b8c7d4" stroke-width="2"/>
      <rect x="110" y="156" width="22" height="16" rx="3" fill="none" stroke="#b8c7d4" stroke-width="2"/>
      <line x1="116" y1="150" x2="116" y2="160" stroke="#1cb0f6" stroke-width="3" stroke-linecap="round"/>`,
  },
  capa: {
    atras: `<path d="M62 126 L24 192 L176 192 L138 126 Z" fill="#e53935" ${TRAZO}/>`,
    delante: `
      <circle cx="70" cy="127" r="6" fill="#ffc800" ${TRAZO}/>
      <circle cx="130" cy="127" r="6" fill="#ffc800" ${TRAZO}/>`,
  },
};

// ---------- Accesorios (se dibujan sobre la cabeza) ----------
const ACCESORIOS = {
  gafas: `
    <circle cx="84" cy="82" r="14" fill="#ffffff" fill-opacity="0.3" stroke="#222222" stroke-width="4"/>
    <circle cx="116" cy="82" r="14" fill="#ffffff" fill-opacity="0.3" stroke="#222222" stroke-width="4"/>
    <line x1="98" y1="82" x2="102" y2="82" stroke="#222222" stroke-width="4"/>`,
  gorra: `
    <path d="M54 64 Q54 28 100 28 Q146 28 146 64 Z" fill="#e53935" ${TRAZO}/>
    <rect x="58" y="60" width="84" height="9" rx="4.5" fill="#b71c1c"/>
    <circle cx="100" cy="28" r="4" fill="#b71c1c"/>`,
  audifonos: `
    <path d="M48 86 Q48 34 100 34 Q152 34 152 86" fill="none" stroke="#333333" stroke-width="8" stroke-linecap="round"/>
    <rect x="38" y="70" width="16" height="32" rx="8" fill="#ff4b4b" stroke="#333333" stroke-width="3"/>
    <rect x="146" y="70" width="16" height="32" rx="8" fill="#ff4b4b" stroke="#333333" stroke-width="3"/>`,
  sombrero: `
    <polygon points="100,4 66,58 134,58" fill="#6a1b9a" ${TRAZO}/>
    <ellipse cx="100" cy="58" rx="50" ry="9" fill="#4a148c"/>
    <circle cx="96" cy="34" r="4" fill="#ffc800"/>
    <circle cx="108" cy="46" r="3" fill="#ffc800"/>`,
  corona: `
    <path d="M62 54 L62 28 L81 42 L100 20 L119 42 L138 28 L138 54 Z" fill="#ffc800" stroke="#b38600" stroke-width="3" stroke-linejoin="round"/>
    <rect x="62" y="48" width="76" height="8" fill="#e0a800"/>
    <circle cx="100" cy="38" r="4" fill="#ff4b4b"/>`,
};

// Busca una clave en un diccionario de forma segura (ignora claves raras como "constructor")
function buscar(diccionario, clave) {
  if (clave && Object.prototype.hasOwnProperty.call(diccionario, clave)) {
    return diccionario[clave];
  }
  return null;
}

// Construye el texto SVG completo. config = { color, ropa, accesorio }
function construirSvg(config) {
  // Solo aceptamos colores con formato #rrggbb (así nunca se cuela otra cosa en el SVG)
  const color = /^#[0-9a-fA-F]{6}$/.test(config.color || "") ? config.color : COLOR_POR_DEFECTO;
  const ropa = buscar(ROPAS, config.ropa) || { atras: "", delante: "" };
  const accesorio = buscar(ACCESORIOS, config.accesorio) || "";

  return `
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Avatar">
  <circle cx="100" cy="100" r="98" fill="#e8f4fd"/>

  ${ropa.atras}

  <!-- antena -->
  <line x1="100" y1="30" x2="100" y2="50" stroke="#555555" stroke-width="4" stroke-linecap="round"/>
  <circle cx="100" cy="26" r="7" fill="#ff4b4b"/>

  <!-- brazos y pies -->
  <rect x="44" y="128" width="14" height="36" rx="7" fill="${color}" ${TRAZO}/>
  <rect x="142" y="128" width="14" height="36" rx="7" fill="${color}" ${TRAZO}/>
  <rect x="70" y="174" width="26" height="14" rx="7" fill="${color}" ${TRAZO}/>
  <rect x="104" y="174" width="26" height="14" rx="7" fill="${color}" ${TRAZO}/>

  <!-- cuerpo -->
  <rect x="62" y="122" width="76" height="58" rx="18" fill="${color}" ${TRAZO}/>
  <circle cx="100" cy="150" r="8" fill="#ffffff" fill-opacity="0.55"/>

  <!-- cabeza, pantalla, ojos y boca -->
  <rect x="50" y="48" width="100" height="72" rx="24" fill="${color}" ${TRAZO}/>
  <rect x="62" y="62" width="76" height="44" rx="16" fill="#ffffff" fill-opacity="0.92"/>
  <circle cx="84" cy="82" r="8" fill="#2b2b2b"/>
  <circle cx="116" cy="82" r="8" fill="#2b2b2b"/>
  <circle cx="87" cy="79" r="2.5" fill="#ffffff"/>
  <circle cx="119" cy="79" r="2.5" fill="#ffffff"/>
  <path d="M86 96 Q100 106 114 96" fill="none" stroke="#2b2b2b" stroke-width="3.5" stroke-linecap="round"/>

  ${ropa.delante}
  ${accesorio}
</svg>`;
}

// Dibuja el avatar dentro de un elemento de la página
function dibujarAvatar(elemento, config) {
  elemento.innerHTML = construirSvg(config);
}
