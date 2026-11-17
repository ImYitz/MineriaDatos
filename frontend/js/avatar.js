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

// ---------- Colores especiales (degradados) ----------
// Un color normal es un código #rrggbb. Estos nombres se dibujan como degradado.
// Para añadir uno: agrega aquí sus paradas [posición, color] y su fila en catalogo_items.py
// (con el nombre como "valor").
const COLORES_ESPECIALES = {
  arcoiris: [[0, "#ff4b4b"], [0.25, "#ffc800"], [0.5, "#58cc02"], [0.75, "#1cb0f6"], [1, "#a560e8"]],
  galaxia: [[0, "#1a237e"], [0.5, "#7b1fa2"], [1, "#ff5fa2"]],
};
let contadorDegradados = 0;   // cada dibujo necesita un id propio para su degradado

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
  overol: {
    atras: "",
    delante: `
      <rect x="62" y="132" width="76" height="48" rx="14" fill="#3b6fd4" ${TRAZO}/>
      <rect x="76" y="122" width="10" height="18" rx="4" fill="#3b6fd4" ${TRAZO}/>
      <rect x="114" y="122" width="10" height="18" rx="4" fill="#3b6fd4" ${TRAZO}/>
      <circle cx="81" cy="134" r="3.5" fill="#ffc800"/>
      <circle cx="119" cy="134" r="3.5" fill="#ffc800"/>
      <rect x="86" y="152" width="28" height="18" rx="4" fill="#2d58b0"/>
      <line x1="86" y1="158" x2="114" y2="158" stroke="#1f4287" stroke-width="2"/>`,
  },
  chaleco: {
    atras: "",
    delante: `
      <rect x="62" y="122" width="76" height="58" rx="18" fill="#ff9600" ${TRAZO}/>
      <rect x="77" y="124" width="7" height="54" fill="#fff1c9"/>
      <rect x="116" y="124" width="7" height="54" fill="#fff1c9"/>
      <rect x="64" y="150" width="72" height="7" fill="#fff1c9"/>`,
  },
  poncho: {
    atras: "",
    delante: `
      <polygon points="100,120 36,178 164,178" fill="#e8743b" ${TRAZO}/>
      <polygon points="100,138 56,178 144,178" fill="#ffc800"/>
      <polygon points="100,152 72,178 128,178" fill="#58cc02"/>
      <polygon points="100,164 86,178 114,178" fill="#a560e8"/>
      <ellipse cx="100" cy="122" rx="16" ry="5" fill="#c85f2b"/>`,
  },
  smoking: {
    atras: "",
    delante: `
      <rect x="62" y="122" width="76" height="58" rx="18" fill="#222222" ${TRAZO}/>
      <rect x="42" y="126" width="18" height="40" rx="9" fill="#222222" ${TRAZO}/>
      <rect x="140" y="126" width="18" height="40" rx="9" fill="#222222" ${TRAZO}/>
      <polygon points="84,122 116,122 100,168" fill="#ffffff"/>
      <polygon points="88,126 100,132 88,138" fill="#d32f2f"/>
      <polygon points="112,126 100,132 112,138" fill="#d32f2f"/>
      <circle cx="100" cy="132" r="3" fill="#b71c1c"/>
      <circle cx="100" cy="148" r="2.2" fill="#222222"/>
      <circle cx="100" cy="158" r="2.2" fill="#222222"/>`,
  },
  armadura: {
    atras: "",
    delante: `
      <rect x="62" y="122" width="76" height="58" rx="18" fill="#b0bec5" ${TRAZO}/>
      <path d="M76 128 L124 128 L118 170 L82 170 Z" fill="#cfd8dc" stroke="#78909c" stroke-width="3" stroke-linejoin="round"/>
      <circle cx="100" cy="148" r="8" fill="#ffc800" stroke="#b38600" stroke-width="2"/>
      <ellipse cx="52" cy="131" rx="14" ry="10" fill="#90a4ae" ${TRAZO}/>
      <ellipse cx="148" cy="131" rx="14" ry="10" fill="#90a4ae" ${TRAZO}/>`,
  },
  astronauta: {
    atras: "",
    delante: `
      <rect x="62" y="122" width="76" height="58" rx="18" fill="#f5f5f5" ${TRAZO}/>
      <rect x="42" y="126" width="18" height="40" rx="9" fill="#f5f5f5" ${TRAZO}/>
      <rect x="140" y="126" width="18" height="40" rx="9" fill="#f5f5f5" ${TRAZO}/>
      <rect x="64" y="158" width="72" height="8" fill="#ff9600"/>
      <rect x="86" y="130" width="28" height="16" rx="3" fill="#455a64"/>
      <circle cx="93" cy="138" r="2.5" fill="#58cc02"/>
      <circle cx="100" cy="138" r="2.5" fill="#ff4b4b"/>
      <circle cx="107" cy="138" r="2.5" fill="#1cb0f6"/>`,
  },
};

// ---------- Accesorios (se dibujan sobre la cabeza o el cuello) ----------
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
  lazo: `
    <polygon points="74,52 52,40 52,64" fill="#ff5fa2" ${TRAZO}/>
    <polygon points="74,52 96,40 96,64" fill="#ff5fa2" ${TRAZO}/>
    <circle cx="74" cy="52" r="6" fill="#e0407f"/>`,
  bigote: `
    <path d="M80 95 Q90 86 100 93 Q110 86 120 95 Q110 101 100 96 Q90 101 80 95 Z" fill="#4b2e1e"/>`,
  bufanda: `
    <rect x="62" y="114" width="76" height="14" rx="7" fill="#e53935" ${TRAZO}/>
    <rect x="78" y="114" width="6" height="14" fill="#b71c1c"/>
    <rect x="116" y="114" width="6" height="14" fill="#b71c1c"/>
    <rect x="112" y="122" width="14" height="34" rx="5" fill="#e53935" ${TRAZO}/>
    <rect x="112" y="138" width="14" height="5" fill="#b71c1c"/>`,
  pirata: `
    <line x1="56" y1="70" x2="144" y2="106" stroke="#222222" stroke-width="4" stroke-linecap="round"/>
    <ellipse cx="84" cy="82" rx="13" ry="11" fill="#1a1a1a" stroke="#000000" stroke-opacity="0.4" stroke-width="2"/>`,
  lentes_sol: `
    <rect x="68" y="72" width="30" height="20" rx="8" fill="#1a1a1a"/>
    <rect x="102" y="72" width="30" height="20" rx="8" fill="#1a1a1a"/>
    <rect x="96" y="76" width="8" height="4" fill="#1a1a1a"/>
    <line x1="74" y1="77" x2="82" y2="77" stroke="#ffffff" stroke-opacity="0.55" stroke-width="3" stroke-linecap="round"/>
    <line x1="108" y1="77" x2="116" y2="77" stroke="#ffffff" stroke-opacity="0.55" stroke-width="3" stroke-linecap="round"/>`,
  gorro_invierno: `
    <path d="M54 62 Q54 26 100 26 Q146 26 146 62 Z" fill="#e53935" ${TRAZO}/>
    <rect x="52" y="56" width="96" height="12" rx="6" fill="#b71c1c"/>
    <circle cx="100" cy="20" r="9" fill="#ffffff" ${TRAZO}/>`,
  orejas_gato: `
    <polygon points="56,58 60,22 90,48" fill="#555555" ${TRAZO}/>
    <polygon points="144,58 140,22 110,48" fill="#555555" ${TRAZO}/>
    <polygon points="64,50 66,33 80,46" fill="#ffb3d3"/>
    <polygon points="136,50 134,33 120,46" fill="#ffb3d3"/>`,
  cuernos: `
    <path d="M66 54 Q50 38 58 20 Q76 30 84 50 Z" fill="#e53935" ${TRAZO}/>
    <path d="M134 54 Q150 38 142 20 Q124 30 116 50 Z" fill="#e53935" ${TRAZO}/>`,
  casco: `
    <path d="M52 66 Q52 30 100 30 Q148 30 148 66 Z" fill="#ffc800" stroke="#b38600" stroke-width="3" stroke-linejoin="round"/>
    <rect x="46" y="62" width="108" height="9" rx="4.5" fill="#e0a800"/>
    <rect x="92" y="28" width="16" height="36" rx="4" fill="#e0a800"/>`,
  antifaz: `
    <rect x="58" y="68" width="84" height="28" rx="14" fill="#d32f2f" ${TRAZO}/>
    <ellipse cx="84" cy="82" rx="11" ry="9" fill="#ffffff"/>
    <ellipse cx="116" cy="82" rx="11" ry="9" fill="#ffffff"/>
    <circle cx="84" cy="82" r="6.5" fill="#2b2b2b"/>
    <circle cx="116" cy="82" r="6.5" fill="#2b2b2b"/>
    <circle cx="87" cy="79" r="2" fill="#ffffff"/>
    <circle cx="119" cy="79" r="2" fill="#ffffff"/>`,
  chef: `
    <ellipse cx="76" cy="38" rx="20" ry="16" fill="#ffffff" ${TRAZO}/>
    <ellipse cx="124" cy="38" rx="20" ry="16" fill="#ffffff" ${TRAZO}/>
    <ellipse cx="100" cy="30" rx="22" ry="18" fill="#ffffff" ${TRAZO}/>
    <rect x="62" y="46" width="76" height="14" rx="4" fill="#ffffff" ${TRAZO}/>`,
  halo: `
    <ellipse cx="100" cy="14" rx="30" ry="7" fill="none" stroke="#ffc800" stroke-width="6"/>`,
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
  // Solo aceptamos colores #rrggbb o un degradado de COLORES_ESPECIALES (así nunca se cuela otra cosa en el SVG)
  const especial = buscar(COLORES_ESPECIALES, config.color);
  let color = /^#[0-9a-fA-F]{6}$/.test(config.color || "") ? config.color : COLOR_POR_DEFECTO;
  let definiciones = "";
  if (especial) {
    const id = "degradado-avatar-" + (++contadorDegradados);
    const paradas = especial
      .map((p) => '<stop offset="' + p[0] + '" stop-color="' + p[1] + '"/>')
      .join("");
    definiciones = '<defs><linearGradient id="' + id + '" x1="0" y1="0" x2="1" y2="1">' + paradas + "</linearGradient></defs>";
    color = "url(#" + id + ")";
  }
  const ropa = buscar(ROPAS, config.ropa) || { atras: "", delante: "" };
  const accesorio = buscar(ACCESORIOS, config.accesorio) || "";

  return `
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Avatar">
  ${definiciones}
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
