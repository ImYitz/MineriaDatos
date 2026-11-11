// Panel "Mis datos de estudio": riesgo de abandono, recomendación y gráficos del historial.
// Todo se calcula en el servidor (GET /api/estudio); aquí solo se dibuja.

const NOMBRES_TIPO = {
  lecciones: "Lecciones del curso",
  laboratorios: "Laboratorios",
  r: "Aprende R",
  libre: "Modo libre",
};
const NOMBRES_NIVEL = { bajo: "Riesgo bajo", medio: "Riesgo medio", alto: "Riesgo alto" };
const PUNTAJE_ACEPTABLE = 70;

function crear(etiqueta, clase, texto) {
  const el = document.createElement(etiqueta);
  if (clase) el.className = clase;
  if (texto !== undefined) el.textContent = texto;
  return el;
}

function vaciar(id) {
  const el = document.getElementById(id);
  el.textContent = "";
  return el;
}

// ---------- 1) Riesgo ----------

function dibujarRiesgo(riesgo) {
  const etiqueta = document.getElementById("riesgo-nivel");
  etiqueta.textContent = NOMBRES_NIVEL[riesgo.nivel] || riesgo.nivel;
  etiqueta.className = "etiqueta-riesgo riesgo-" + riesgo.nivel;

  document.getElementById("riesgo-porcentaje").textContent = riesgo.probabilidad + " %";
  const barra = document.getElementById("riesgo-barra");
  barra.style.width = riesgo.probabilidad + "%";
  barra.className = "barra-relleno riesgo-" + riesgo.nivel;

  document.getElementById("riesgo-mensaje").textContent = riesgo.mensaje;
  document.getElementById("riesgo-aviso").classList.toggle("oculto", riesgo.datos_suficientes);

  const lista = vaciar("lista-factores");
  for (const factor of riesgo.factores) {
    const li = crear("li", factor.efecto);
    li.appendChild(crear("span", "marca", factor.efecto === "sube" ? "▲" : factor.efecto === "baja" ? "▼" : "•"));
    const texto = crear("div");
    texto.appendChild(document.createTextNode(factor.texto));
    texto.appendChild(crear("small", "",
      factor.efecto === "sube" ? "Aumenta tu riesgo"
        : factor.efecto === "baja" ? "Reduce tu riesgo" : "Casi no influye"));
    li.appendChild(texto);
    lista.appendChild(li);
  }
}

// ---------- 2) Recomendación ----------

function dibujarRecomendacion(reco) {
  document.getElementById("reco-titulo").textContent = reco.titulo;
  document.getElementById("reco-texto").textContent = reco.texto;
  const enlace = document.getElementById("reco-enlace");
  enlace.href = reco.enlace;
  enlace.textContent = reco.boton;

  const relacionada = document.getElementById("reco-relacionada");
  relacionada.textContent = "";
  if (reco.relacionada) {
    relacionada.appendChild(document.createTextNode("Para practicar este tema: "));
    const a = crear("a", "", reco.relacionada.titulo);
    a.href = reco.relacionada.enlace;
    relacionada.appendChild(a);
    relacionada.classList.remove("oculto");
  } else {
    relacionada.classList.add("oculto");
  }
}

// ---------- 3) Perfil de estudiante (K-means) ----------

const COLORES_GRUPO = ["#58cc02", "#1cb0f6", "#ff9600", "#a560e8", "#ff4b4b"];

function dibujarGraficoSegmentos(seg) {
  const canvas = document.getElementById("seg-lienzo");
  const r = window.devicePixelRatio || 1;
  canvas.width = 600 * r;
  canvas.height = 320 * r;
  const ctx = canvas.getContext && canvas.getContext("2d");
  if (!ctx) return;
  ctx.scale(r, r);
  const A = { x: 52, y: 12, w: 530, h: 256 };
  const px = (v) => A.x + (v / 14) * A.w;
  const py = (v) => A.y + A.h - (v / 100) * A.h;

  ctx.font = "11px 'Segoe UI', Arial, sans-serif";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const yy = Math.round(py(i * 25)) + 0.5;
    ctx.strokeStyle = "#eeeeee";
    ctx.beginPath(); ctx.moveTo(A.x, yy); ctx.lineTo(A.x + A.w, yy); ctx.stroke();
    ctx.fillStyle = "#777777"; ctx.textAlign = "right"; ctx.textBaseline = "middle";
    ctx.fillText(String(i * 25), A.x - 6, yy);
  }
  for (let v = 0; v <= 14; v += 2) {
    ctx.fillStyle = "#777777"; ctx.textAlign = "center"; ctx.textBaseline = "top";
    ctx.fillText(String(v), px(v), A.y + A.h + 5);
  }
  ctx.strokeStyle = "#cccccc";
  ctx.strokeRect(A.x + 0.5, A.y + 0.5, A.w, A.h);
  ctx.fillStyle = "#555555";
  ctx.font = "bold 12px 'Segoe UI', Arial, sans-serif";
  ctx.textAlign = "center"; ctx.textBaseline = "alphabetic";
  ctx.fillText("Días con estudio en los últimos 14", A.x + A.w / 2, A.y + A.h + 36);
  ctx.save();
  ctx.translate(14, A.y + A.h / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText("Puntaje medio (%)", 0, 0);
  ctx.restore();

  // Pequeña separación para que los puntos iguales no se tapen entre sí
  const sacudida = (i, escala) => (((i * 9301 + 49297) % 233280) / 233280 - 0.5) * escala;
  seg.puntos.forEach((p, i) => {
    ctx.beginPath();
    ctx.arc(px(Math.max(0, Math.min(14, p.x + sacudida(i, 0.5)))), py(Math.max(0, Math.min(100, p.y + sacudida(i * 7 + 3, 3)))), 3.6, 0, Math.PI * 2);
    ctx.fillStyle = COLORES_GRUPO[p.grupo % COLORES_GRUPO.length] + "aa";
    ctx.fill();
  });
  if (seg.mi_punto) {
    const x = px(seg.mi_punto.x), y = py(seg.mi_punto.y);
    ctx.beginPath(); ctx.arc(x, y, 9, 0, Math.PI * 2);
    ctx.fillStyle = COLORES_GRUPO[seg.mi_punto.grupo % COLORES_GRUPO.length];
    ctx.fill();
    ctx.lineWidth = 3; ctx.strokeStyle = "#222222"; ctx.stroke();
    ctx.fillStyle = "#222222";
    ctx.font = "bold 13px 'Segoe UI', Arial, sans-serif";
    ctx.textAlign = "left"; ctx.textBaseline = "bottom";
    ctx.fillText("Tú", x + 12, y - 8);
  }
}

function dibujarSegmentacion(seg) {
  const estado = document.getElementById("seg-estado");
  const contenido = document.getElementById("seg-contenido");
  if (!seg) {
    estado.textContent = "Todavía no hay suficientes estudiantes para formar grupos (hacen falta al menos 20 con actividad). " +
      "Ejecuta sembrar_estudiantes.py para crear estudiantes simulados.";
    estado.classList.remove("oculto");
    contenido.classList.add("oculto");
    return;
  }
  estado.classList.add("oculto");
  contenido.classList.remove("oculto");

  const grupo = seg.mi_grupo === null ? null : seg.grupos.find((g) => g.id === seg.mi_grupo);
  const mi = document.getElementById("seg-mi-grupo");
  mi.textContent = "";
  if (grupo) {
    mi.appendChild(document.createTextNode("Perteneces al grupo "));
    mi.appendChild(crear("strong", "", "«" + grupo.nombre + "»"));
    mi.appendChild(document.createTextNode(". " + grupo.descripcion));
  } else {
    mi.textContent = "Todavía no tienes actividad, así que aún no se te puede ubicar en ningún grupo.";
  }

  dibujarGraficoSegmentos(seg);

  const leyenda = vaciar("seg-leyenda");
  for (const g of seg.grupos) {
    const item = crear("span");
    const punto = crear("span", "punto");
    punto.style.background = COLORES_GRUPO[g.id % COLORES_GRUPO.length];
    item.appendChild(punto);
    item.appendChild(document.createTextNode(g.nombre));
    leyenda.appendChild(item);
  }

  const caja = vaciar("seg-tabla");
  const tabla = crear("table", "tabla-estudio");
  const cabecera = crear("thead");
  const filaCab = crear("tr");
  for (const h of ["Grupo", "Estudiantes", "Días de estudio (de 14)", "Días sin estudiar", "Puntaje medio", "Tipos de actividad"]) {
    filaCab.appendChild(crear("th", "", h));
  }
  cabecera.appendChild(filaCab);
  tabla.appendChild(cabecera);
  const cuerpo = crear("tbody");
  for (const g of seg.grupos) {
    const tr = crear("tr", g.id === seg.mi_grupo ? "mi-grupo" : "");
    for (const v of [g.nombre, g.tamano + " (" + g.porcentaje + " %)", g.dias_activos_14, g.dias_sin_estudiar,
                     g.puntaje_medio + " %", g.variedad]) {
      tr.appendChild(crear("td", "", String(v)));
    }
    cuerpo.appendChild(tr);
  }
  tabla.appendChild(cuerpo);
  caja.appendChild(tabla);

  const siluetas = seg.siluetas.map((s) => "k = " + s.k + ": " + s.silueta).join(" · ");
  document.getElementById("seg-metodo").textContent =
    "Método: K-means (aprendizaje no supervisado) sobre " + seg.total + " estudiantes, usando cuatro variables " +
    "(constancia, días sin estudiar, puntaje medio y variedad). Se probaron varios números de grupos y se eligió " +
    "k = " + seg.k + " por tener la mejor silueta (" + siluetas + "; cuanto más cerca de 1, mejor separados quedan los grupos). " +
    "Los nombres de los grupos se asignan según el centroide de cada uno." +
    (seg.simulados > 0 ? " Ojo: " + seg.simulados + " de esos estudiantes son simulados." : "");
}

// ---------- 4) Datos ----------

function dibujarKpis(res) {
  const kpis = vaciar("kpis");
  const datos = [
    [res.total_actividades, "Actividades terminadas"],
    [res.dias_activos, "Días en que estudiaste"],
    [res.puntaje_medio === null ? "—" : res.puntaje_medio + " %", "Puntaje medio"],
    [res.racha_actual, res.racha_actual === 1 ? "Día de racha" : "Días de racha"],
  ];
  for (const [valor, nombre] of datos) {
    const kpi = crear("div", "kpi");
    kpi.appendChild(crear("strong", "", String(valor)));
    kpi.appendChild(crear("span", "", nombre));
    kpis.appendChild(kpi);
  }
}

function dibujarActividad(dias) {
  const grafico = vaciar("grafico-dias");
  const maximo = Math.max(1, ...dias.map((d) => d.actividades));
  for (const dia of dias) {
    const fecha = new Date(dia.fecha + "T00:00:00");
    const columna = crear("div", "col-dia");
    columna.title = fecha.toLocaleDateString("es-CO", { day: "numeric", month: "long" }) +
      ": " + dia.actividades + (dia.actividades === 1 ? " actividad" : " actividades");
    const area = crear("div", "area-barra");
    const barra = crear("div", "barra-dia" + (dia.actividades === 0 ? " vacia" : ""));
    barra.style.height = (dia.actividades === 0 ? 0 : Math.max(8, (dia.actividades / maximo) * 100)) + "%";
    area.appendChild(barra);
    columna.appendChild(area);
    columna.appendChild(crear("small", "", String(fecha.getDate())));
    grafico.appendChild(columna);
  }
}

function dibujarPorTipo(porTipo) {
  const caja = vaciar("por-tipo");
  for (const clave of Object.keys(NOMBRES_TIPO)) {
    const fila = crear("div", "fila-tipo");
    fila.appendChild(crear("span", "", NOMBRES_TIPO[clave]));
    fila.appendChild(crear("strong", "", String(porTipo[clave] || 0)));
    caja.appendChild(fila);
  }
}

function dibujarLecciones(lecciones) {
  const caja = vaciar("grafico-lecciones");
  for (const l of lecciones) {
    const fila = crear("div", "fila-leccion");
    const nombre = crear("span", "nombre", l.orden + ". " + l.titulo);
    nombre.title = l.titulo;
    const pista = crear("div", "pista");
    const relleno = crear("div", "relleno" + (l.mejor_puntaje !== null && l.mejor_puntaje < PUNTAJE_ACEPTABLE ? " debil" : ""));
    relleno.style.width = (l.mejor_puntaje || 0) + "%";
    pista.appendChild(relleno);
    fila.appendChild(nombre);
    fila.appendChild(pista);
    fila.appendChild(crear("span", "valor", l.mejor_puntaje === null ? "Pendiente" : l.mejor_puntaje + " %"));
    caja.appendChild(fila);
  }
}

// ---------- 5) Cómo se calculó ----------

function dibujarModelo(m) {
  const total = m.datos_entrenamiento + m.datos_prueba;
  const deBase = m.origen === "base_datos";
  const pasos = vaciar("pasos-modelo");
  const textos = [
    "Datos: el historial de lecciones, laboratorios, prácticas de R y modo libre (fechas y puntajes) de " +
      (deBase ? "los " + total + " estudiantes de la base de datos." : "estudiantes simulados en memoria."),
    "Preparación: se convierte en 6 variables: días sin estudiar, constancia en los últimos 14 días, " +
      "puntaje medio, tendencia de los resultados, variedad de actividades y racha. " +
      (deBase ? "Se elige una fecha de corte (hace 14 días): las variables salen de lo que pasó hasta ese día " +
        "y la etiqueta «abandona» significa que no volvió a estudiar en los 14 días siguientes." : ""),
    "Modelo: " + m.algoritmo + ", un algoritmo de clasificación (abandona / continúa) entrenado con " +
      m.datos_entrenamiento + " estudiantes. Cada variable tiene un peso; por eso puedes ver qué influye más.",
    "Evaluación: se probó con " + m.datos_prueba + " estudiantes que no vio al entrenar. " +
      "Acierta el " + m.exactitud + " % de las veces, frente al " + m.exactitud_base +
      " % de un modelo que siempre responde lo más frecuente.",
    "Uso: tus datos se pasan por el modelo y se obtiene tu probabilidad de abandono; la recomendación " +
      "sale de tus puntajes por lección.",
  ];
  for (const t of textos) pasos.appendChild(crear("li", "", t));

  const aviso = document.getElementById("aviso-modelo");
  if (!deBase) {
    aviso.textContent = "Importante: todavía no hay suficientes estudiantes en la base de datos, así que el modelo " +
      "se entrenó con estudiantes simulados en memoria. Ejecuta sembrar_estudiantes.py para entrenarlo con datos de la base.";
  } else if (m.simulados > 0) {
    aviso.textContent = "Importante: " + m.simulados + " de los " + total + " estudiantes usados son simulados " +
      "(sim_001, sim_002...). Es una demostración del proceso de minería de datos, no un diagnóstico real, " +
      "y con datos simulados la exactitud sale más alta de lo que sería con personas reales.";
  } else {
    aviso.textContent = "Modelo entrenado solo con estudiantes reales de la base de datos.";
  }

  const caja = vaciar("tabla-modelo");
  const tabla = crear("table", "tabla-estudio");
  const cabecera = crear("thead");
  const filaCab = crear("tr");
  for (const h of ["", "Predice: continúa", "Predice: abandona"]) filaCab.appendChild(crear("th", "", h));
  cabecera.appendChild(filaCab);
  tabla.appendChild(cabecera);
  const cuerpo = crear("tbody");
  const nombres = ["Real: continúa", "Real: abandona"];
  m.matriz.forEach((fila, real) => {
    const tr = crear("tr");
    tr.appendChild(crear("td", "", nombres[real]));
    for (const valor of fila) tr.appendChild(crear("td", "", String(valor)));
    cuerpo.appendChild(tr);
  });
  tabla.appendChild(cuerpo);
  caja.appendChild(tabla);
  caja.appendChild(crear("p", "texto-suave",
    "Exactitud: " + m.exactitud + " % · Precisión: " + m.precision + " % (de los que marca en riesgo, " +
    "cuántos lo estaban) · Sensibilidad: " + m.sensibilidad + " % (de los que estaban en riesgo, cuántos detecta)."));
}

// ---------- Inicio ----------

async function cargar() {
  try {
    const res = await pedirApi("/api/estudio");
    dibujarRiesgo(res.riesgo);
    dibujarRecomendacion(res.recomendacion);
    dibujarSegmentacion(res.segmentacion);
    dibujarKpis(res);
    dibujarActividad(res.actividad_14);
    dibujarPorTipo(res.por_tipo);
    dibujarLecciones(res.puntajes_lecciones);
    dibujarModelo(res.modelo);
    document.getElementById("contenido-estudio").classList.remove("oculto");
  } catch (error) {
    document.getElementById("mensaje-error").textContent =
      "No se pudieron cargar tus datos de estudio. ¿Reiniciaste el servidor?";
  }
}

if (exigirSesion()) {
  cargar();
}
