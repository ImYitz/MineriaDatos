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

// ---------- 3) Datos ----------

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

// ---------- 4) Cómo se calculó ----------

function dibujarModelo(m) {
  const pasos = vaciar("pasos-modelo");
  const textos = [
    "Datos: tu historial de lecciones, laboratorios, prácticas de R y modo libre (fechas y puntajes).",
    "Preparación: se convierte en 6 variables: días sin estudiar, constancia en los últimos 14 días, " +
      "puntaje medio, tendencia de los resultados, variedad de actividades y racha.",
    "Modelo: " + m.algoritmo + ", un algoritmo de clasificación (abandona / continúa) entrenado con " +
      m.datos_entrenamiento + " estudiantes simulados. Cada variable tiene un peso; por eso puedes ver qué influye más.",
    "Evaluación: se probó con " + m.datos_prueba + " estudiantes que no vio al entrenar. " +
      "Acierta el " + m.exactitud + " % de las veces, frente al " + m.exactitud_base +
      " % de un modelo que siempre responde lo más frecuente.",
    "Uso: tus datos se pasan por el modelo y se obtiene tu probabilidad de abandono; la recomendación " +
      "sale de tus puntajes por lección.",
  ];
  for (const t of textos) pasos.appendChild(crear("li", "", t));

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
