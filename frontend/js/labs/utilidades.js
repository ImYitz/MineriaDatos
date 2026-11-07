// Herramientas compartidas por los laboratorios interactivos.
// Cada laboratorio se registra aquí:  LABS["codigo"] = { montar(contenedor) { ... } }

const LABS = {};

const PALETA = ["#1cb0f6", "#ff9600", "#a560e8", "#58cc02", "#ff4b4b", "#ffc800"];

// ---------- Números y estadística ----------

// Generador de números "aleatorios" repetibles: con la misma semilla siempre da los
// mismos datos (así las preguntas del laboratorio siempre tienen sentido).
function generadorAleatorio(semilla) {
  let a = semilla >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Número con distribución normal (campana de Gauss), método Box-Muller
function normalAleatoria(azar, media, desv) {
  const u = 1 - azar();
  const v = azar();
  return media + desv * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

function limitar(valor, minimo, maximo) {
  return Math.min(maximo, Math.max(minimo, valor));
}

function promedio(valores) {
  return valores.reduce((s, v) => s + v, 0) / (valores.length || 1);
}

function estadisticas(valores) {
  const orden = valores.slice().sort((a, b) => a - b);
  const n = orden.length;
  const media = promedio(valores);
  const varianza = promedio(valores.map((v) => (v - media) * (v - media)));
  const mediana = n % 2 ? orden[(n - 1) / 2] : (orden[n / 2 - 1] + orden[n / 2]) / 2;
  return { n, min: orden[0], max: orden[n - 1], media, mediana, desv: Math.sqrt(varianza) };
}

function correlacion(xs, ys) {
  const mx = promedio(xs);
  const my = promedio(ys);
  let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < xs.length; i++) {
    sxy += (xs[i] - mx) * (ys[i] - my);
    sxx += (xs[i] - mx) * (xs[i] - mx);
    syy += (ys[i] - my) * (ys[i] - my);
  }
  return sxy / (Math.sqrt(sxx * syy) || 1);
}

function distancia2(a, b) {
  const dx = a[0] - b[0];
  const dy = a[1] - b[1];
  return dx * dx + dy * dy;
}

// Número legible: 1234.5 -> "1.235", 12.3456 -> "12.35"
function formatearNumero(v) {
  const a = Math.abs(v);
  if (a >= 1000) return Math.round(v).toLocaleString("es-CO");
  if (a >= 100) return String(Math.round(v * 10) / 10);
  return String(Math.round(v * 100) / 100);
}

// ---------- Elementos de la página ----------

function crearElemento(etiqueta, clase, texto) {
  const el = document.createElement(etiqueta);
  if (clase) el.className = clase;
  if (texto !== undefined) el.textContent = texto;
  return el;
}

function crearBoton(texto, alHacerClic, clase) {
  const boton = crearElemento("button", clase || "lab-boton", texto);
  boton.type = "button";
  boton.addEventListener("click", alHacerClic);
  return boton;
}

// Grupo de botones donde solo uno está activo. opciones = [{ id, texto }]
function crearSelector(opciones, inicial, alCambiar) {
  const caja = crearElemento("div", "lab-grupo");
  const botones = {};
  function marcar(id) {
    for (const clave in botones) botones[clave].classList.toggle("activo", clave === id);
  }
  for (const opcion of opciones) {
    botones[opcion.id] = crearBoton(opcion.texto, () => {
      marcar(opcion.id);
      alCambiar(opcion.id);
    });
    caja.appendChild(botones[opcion.id]);
  }
  marcar(inicial);
  return caja;
}

function crearDeslizador(texto, minimo, maximo, paso, valor, alCambiar, sufijo) {
  const caja = crearElemento("label", "lab-deslizador");
  const etiqueta = crearElemento("span");
  const entrada = document.createElement("input");
  entrada.type = "range";
  entrada.min = minimo;
  entrada.max = maximo;
  entrada.step = paso;
  entrada.value = valor;
  const mostrar = () => { etiqueta.textContent = texto + ": " + entrada.value + (sufijo || ""); };
  entrada.addEventListener("input", () => {
    mostrar();
    alCambiar(Number(entrada.value));
  });
  mostrar();
  caja.appendChild(etiqueta);
  caja.appendChild(entrada);
  return caja;
}

function tablaSimple(encabezados, filas) {
  const caja = crearElemento("div", "lab-tabla-caja");
  const tabla = crearElemento("table", "lab-tabla");
  const cabecera = document.createElement("thead");
  const filaCabecera = document.createElement("tr");
  for (const h of encabezados) filaCabecera.appendChild(crearElemento("th", "", h));
  cabecera.appendChild(filaCabecera);
  tabla.appendChild(cabecera);

  const cuerpo = document.createElement("tbody");
  for (const fila of filas) {
    const tr = document.createElement("tr");
    for (const celda of fila) tr.appendChild(crearElemento("td", "", String(celda)));
    cuerpo.appendChild(tr);
  }
  tabla.appendChild(cuerpo);
  caja.appendChild(tabla);
  return caja;
}

// Leyenda: [{ color, texto }]
function crearLeyenda(elementos) {
  const caja = crearElemento("div", "lab-leyenda");
  for (const e of elementos) {
    const item = crearElemento("span");
    const punto = crearElemento("span", "punto");
    punto.style.background = e.color;
    item.appendChild(punto);
    item.appendChild(document.createTextNode(e.texto));
    caja.appendChild(item);
  }
  return caja;
}

// ---------- Gráficos con canvas ----------

const AREA = { x: 58, y: 12, w: 528, h: 304 };   // zona de dibujo dentro del lienzo de 600 x 360

// Lienzo nítido en pantallas de alta densidad; el CSS lo adapta al ancho disponible.
function crearLienzo(ancho, alto) {
  const canvas = document.createElement("canvas");
  const r = window.devicePixelRatio || 1;
  canvas.width = ancho * r;
  canvas.height = alto * r;
  canvas.className = "lab-lienzo";
  const ctx = canvas.getContext("2d");
  ctx.scale(r, r);
  return { canvas, ctx, ancho, alto };
}

// Posición del ratón/dedo en las coordenadas del lienzo (600 x 360)
function posicionEnLienzo(evento, lienzo) {
  const caja = lienzo.canvas.getBoundingClientRect();
  return {
    x: ((evento.clientX - caja.left) * lienzo.ancho) / caja.width,
    y: ((evento.clientY - caja.top) * lienzo.alto) / caja.height,
  };
}

// Escala lineal: convierte un valor de los datos en una posición en pantalla (y al revés)
function crearEscala(dominio, rango) {
  const d0 = dominio[0], d1 = dominio[1], r0 = rango[0], r1 = rango[1];
  const f = (v) => r0 + ((v - d0) * (r1 - r0)) / (d1 - d0 || 1);
  f.inversa = (p) => d0 + ((p - r0) * (d1 - d0)) / (r1 - r0 || 1);
  f.dominio = dominio;
  return f;
}

// Dominio con un poco de margen alrededor de los datos
function ampliar(minimo, maximo, margen) {
  const m = margen === undefined ? 0.08 : margen;
  const d = maximo - minimo || 1;
  return [minimo - d * m, maximo + d * m];
}

function dibujarEjes(ctx, ex, ey, tituloX, tituloY) {
  ctx.save();
  ctx.font = "11px 'Segoe UI', Arial, sans-serif";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const vx = ex.dominio[0] + (i * (ex.dominio[1] - ex.dominio[0])) / 4;
    const px = Math.round(ex(vx)) + 0.5;
    ctx.strokeStyle = "#eeeeee";
    ctx.beginPath(); ctx.moveTo(px, AREA.y); ctx.lineTo(px, AREA.y + AREA.h); ctx.stroke();
    ctx.fillStyle = "#777777";
    ctx.textAlign = "center"; ctx.textBaseline = "top";
    ctx.fillText(formatearNumero(vx), px, AREA.y + AREA.h + 5);

    const vy = ey.dominio[0] + (i * (ey.dominio[1] - ey.dominio[0])) / 4;
    const py = Math.round(ey(vy)) + 0.5;
    ctx.strokeStyle = "#eeeeee";
    ctx.beginPath(); ctx.moveTo(AREA.x, py); ctx.lineTo(AREA.x + AREA.w, py); ctx.stroke();
    ctx.fillStyle = "#777777";
    ctx.textAlign = "right"; ctx.textBaseline = "middle";
    ctx.fillText(formatearNumero(vy), AREA.x - 6, py);
  }
  ctx.strokeStyle = "#cccccc";
  ctx.strokeRect(AREA.x + 0.5, AREA.y + 0.5, AREA.w, AREA.h);

  ctx.fillStyle = "#555555";
  ctx.font = "bold 12px 'Segoe UI', Arial, sans-serif";
  ctx.textAlign = "center"; ctx.textBaseline = "alphabetic";
  ctx.fillText(tituloX, AREA.x + AREA.w / 2, AREA.y + AREA.h + 36);
  ctx.translate(14, AREA.y + AREA.h / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText(tituloY, 0, 0);
  ctx.restore();
}

function dibujarCirculo(ctx, x, y, radio, relleno, borde, grosor) {
  ctx.beginPath();
  ctx.arc(x, y, radio, 0, Math.PI * 2);
  if (relleno) { ctx.fillStyle = relleno; ctx.fill(); }
  if (borde) { ctx.strokeStyle = borde; ctx.lineWidth = grosor || 1.5; ctx.stroke(); }
}
