// Laboratorio: árbol de clasificación (Gini / entropía, profundidad, sobreajuste y matriz de confusión).
(function () {
  const NOMBRES = ["Aprueba", "No aprueba"];
  const COLORES = ["#58cc02", "#ff4b4b"];
  const VARIABLES = ["Nota del parcial", "Asistencia (%)"];
  const ETIQUETAS = ["nota", "asistencia"];
  const SEMILLA = 88;

  // ---------- Datos: 100 estudiantes (70 de entrenamiento y 30 de prueba) ----------
  // Regla real: aprueba quien tiene nota >= 50 y asistencia >= 45, pero el 12 % de los casos
  // tiene "ruido" (resultados que no siguen la regla). Un árbol muy profundo intentará memorizarlo.
  function crearDatos() {
    const azar = generadorAleatorio(SEMILLA);
    const puntos = [];
    for (let i = 0; i < 100; i++) {
      const x = Math.round(5 + 95 * azar());
      const y = Math.round(10 + 90 * azar());
      let clase = x >= 50 && y >= 45 ? 0 : 1;      // 0 = aprueba, 1 = no aprueba
      if (azar() < 0.12) clase = 1 - clase;        // ruido
      puntos.push({ x, y, clase });
    }
    return { entrenamiento: puntos.slice(0, 70), prueba: puntos.slice(70) };
  }

  // ---------- Algoritmo ----------
  function contar(filas) {
    const c = [0, 0];
    for (const f of filas) c[f.clase]++;
    return c;
  }

  // Impureza de un nodo: 0 = todos de la misma clase; mayor = más mezclados
  function impureza(conteos, criterio) {
    const n = conteos[0] + conteos[1];
    if (!n) return 0;
    const p = [conteos[0] / n, conteos[1] / n];
    if (criterio === "gini") return 1 - p[0] * p[0] - p[1] * p[1];
    let h = 0;
    for (const q of p) if (q > 0) h -= q * Math.log2(q);
    return h;
  }

  // Prueba todos los cortes posibles (nota o asistencia) y devuelve el que más reduce la impureza
  function mejorDivision(filas, criterio) {
    const base = impureza(contar(filas), criterio);
    let mejor = null;
    for (let v = 0; v < 2; v++) {
      const clave = v === 0 ? "x" : "y";
      const orden = filas.slice().sort((a, b) => a[clave] - b[clave]);
      const izq = [0, 0];
      const der = contar(filas);
      for (let i = 0; i < orden.length - 1; i++) {
        const c = orden[i].clase;
        izq[c]++; der[c]--;
        if (orden[i][clave] === orden[i + 1][clave]) continue;   // no se puede cortar entre valores iguales
        const nI = i + 1, nD = orden.length - nI;
        const ponderada = (nI * impureza(izq, criterio) + nD * impureza(der, criterio)) / orden.length;
        if (!mejor || ponderada < mejor.ponderada - 1e-12) {
          mejor = {
            variable: v,
            umbral: (orden[i][clave] + orden[i + 1][clave]) / 2,
            ponderada,
            ganancia: base - ponderada,
          };
        }
      }
    }
    return mejor;
  }

  function construir(filas, nivel, maxima, criterio) {
    const conteos = contar(filas);
    const nodo = {
      n: filas.length,
      conteos,
      clase: conteos[0] >= conteos[1] ? 0 : 1,
      impureza: impureza(conteos, criterio),
      hoja: true,
    };
    if (nivel >= maxima || nodo.impureza === 0) return nodo;
    const d = mejorDivision(filas, criterio);
    if (!d || d.ganancia <= 1e-12) return nodo;
    const valor = (f) => (d.variable === 0 ? f.x : f.y);
    nodo.hoja = false;
    nodo.variable = d.variable;
    nodo.umbral = d.umbral;
    nodo.ganancia = d.ganancia;
    nodo.ponderada = d.ponderada;
    nodo.izq = construir(filas.filter((f) => valor(f) <= d.umbral), nivel + 1, maxima, criterio);
    nodo.der = construir(filas.filter((f) => valor(f) > d.umbral), nivel + 1, maxima, criterio);
    return nodo;
  }

  function predecir(nodo, x, y) {
    while (!nodo.hoja) {
      const v = nodo.variable === 0 ? x : y;
      nodo = v <= nodo.umbral ? nodo.izq : nodo.der;
    }
    return nodo.clase;
  }

  function medidas(nodo) {
    if (nodo.hoja) return { nodos: 1, hojas: 1, profundidad: 0 };
    const a = medidas(nodo.izq), b = medidas(nodo.der);
    return {
      nodos: 1 + a.nodos + b.nodos,
      hojas: a.hojas + b.hojas,
      profundidad: 1 + Math.max(a.profundidad, b.profundidad),
    };
  }

  // Aciertos y matriz de confusión (positivo = "Aprueba"): matriz[real][predicho]
  function evaluar(arbol, filas) {
    const matriz = [[0, 0], [0, 0]];
    for (const f of filas) matriz[f.clase][predecir(arbol, f.x, f.y)]++;
    const aciertos = matriz[0][0] + matriz[1][1];
    return { aciertos, total: filas.length, exactitud: filas.length ? aciertos / filas.length : 0, matriz };
  }

  // Cada hoja es una regla "SI ... ENTONCES ..."
  function reglas(nodo, condiciones, salida) {
    if (nodo.hoja) {
      salida.push(
        "SI " + (condiciones.length ? condiciones.join(" Y ") : "siempre") +
        " → " + NOMBRES[nodo.clase] + " (" + nodo.n + " estudiantes)"
      );
      return;
    }
    const nombre = ETIQUETAS[nodo.variable];
    const u = formatearNumero(nodo.umbral);
    reglas(nodo.izq, condiciones.concat([nombre + " ≤ " + u]), salida);
    reglas(nodo.der, condiciones.concat([nombre + " > " + u]), salida);
  }

  function porcentaje(v) {
    return (Math.round(v * 1000) / 10) + " %";
  }

  LABS.arbol = {
    // Se expone para poder probar el algoritmo fuera del navegador
    nucleo: { crearDatos, construir, predecir, evaluar, medidas, impureza },

    montar(contenedor) {
      const datos = crearDatos();
      const ex = crearEscala([0, 100], [AREA.x, AREA.x + AREA.w]);
      const ey = crearEscala([0, 100], [AREA.y + AREA.h, AREA.y]);

      let profundidad = 3;
      let criterio = "gini";
      let mostrarRegiones = true;

      // ---- Interfaz ----
      const controles = crearElemento("div", "lab-controles");
      controles.appendChild(
        crearDeslizador("Profundidad máxima", 1, 8, 1, profundidad, (v) => { profundidad = v; dibujar(); })
      );
      controles.appendChild(
        crearSelector(
          [
            { id: "gini", texto: "Índice Gini" },
            { id: "entropia", texto: "Entropía" },
          ],
          criterio,
          (id) => { criterio = id; dibujar(); }
        )
      );
      const botonRegiones = crearBoton("Mostrar regiones", () => {
        mostrarRegiones = !mostrarRegiones;
        botonRegiones.classList.toggle("activo", mostrarRegiones);
        dibujar();
      });
      botonRegiones.classList.add("activo");
      controles.appendChild(botonRegiones);

      const lienzo = crearLienzo(600, 360);
      const info = crearElemento("div", "lab-info");
      contenedor.appendChild(controles);
      contenedor.appendChild(lienzo.canvas);
      contenedor.appendChild(info);

      // ---- Dibujo ----
      // Líneas de corte: cada división del árbol es una línea vertical u horizontal
      function dibujarCortes(ctx, nodo, x0, x1, y0, y1) {
        if (nodo.hoja) return;
        ctx.beginPath();
        if (nodo.variable === 0) {
          ctx.moveTo(ex(nodo.umbral), ey(y0)); ctx.lineTo(ex(nodo.umbral), ey(y1));
          ctx.stroke();
          dibujarCortes(ctx, nodo.izq, x0, nodo.umbral, y0, y1);
          dibujarCortes(ctx, nodo.der, nodo.umbral, x1, y0, y1);
        } else {
          ctx.moveTo(ex(x0), ey(nodo.umbral)); ctx.lineTo(ex(x1), ey(nodo.umbral));
          ctx.stroke();
          dibujarCortes(ctx, nodo.izq, x0, x1, y0, nodo.umbral);
          dibujarCortes(ctx, nodo.der, x0, x1, nodo.umbral, y1);
        }
      }

      function dibujar() {
        const arbol = construir(datos.entrenamiento, 0, profundidad, criterio);
        const ctx = lienzo.ctx;
        ctx.clearRect(0, 0, lienzo.ancho, lienzo.alto);
        dibujarEjes(ctx, ex, ey, VARIABLES[0], VARIABLES[1]);

        // Regiones: cada celda se pinta con la clase que el árbol predeciría ahí
        if (mostrarRegiones) {
          const columnas = 66, filas = 40;
          const ancho = AREA.w / columnas, alto = AREA.h / filas;
          for (let f = 0; f < filas; f++) {
            for (let c = 0; c < columnas; c++) {
              const clase = predecir(arbol, ((c + 0.5) * 100) / columnas, ((f + 0.5) * 100) / filas);
              ctx.fillStyle = COLORES[clase] + "26";
              ctx.fillRect(AREA.x + c * ancho, AREA.y + AREA.h - (f + 1) * alto, ancho + 0.5, alto + 0.5);
            }
          }
        }

        // Cortes del árbol
        ctx.save();
        ctx.strokeStyle = "#333333";
        ctx.lineWidth = 1.6;
        ctx.setLineDash([7, 4]);
        dibujarCortes(ctx, arbol, 0, 100, 0, 100);
        ctx.restore();

        // Entrenamiento: círculos. Prueba: cuadrados con borde oscuro
        for (const p of datos.entrenamiento) {
          dibujarCirculo(ctx, ex(p.x), ey(p.y), 4.5, COLORES[p.clase], "#ffffff", 1);
        }
        for (const p of datos.prueba) {
          ctx.fillStyle = COLORES[p.clase];
          ctx.strokeStyle = "#222222";
          ctx.lineWidth = 1.8;
          ctx.fillRect(ex(p.x) - 5, ey(p.y) - 5, 10, 10);
          ctx.strokeRect(ex(p.x) - 5, ey(p.y) - 5, 10, 10);
        }

        // ---- Panel de información ----
        const train = evaluar(arbol, datos.entrenamiento);
        const test = evaluar(arbol, datos.prueba);
        const m = medidas(arbol);
        const etiquetaCriterio = criterio === "gini" ? "Gini" : "Entropía";

        info.innerHTML = "";
        info.appendChild(tablaSimple(
          ["", "Exactitud", "Aciertos"],
          [
            ["Entrenamiento (70)", porcentaje(train.exactitud), train.aciertos + " / " + train.total],
            ["Prueba (30)", porcentaje(test.exactitud), test.aciertos + " / " + test.total],
          ]
        ));
        info.appendChild(crearElemento("p", "",
          "Árbol: " + m.nodos + " nodos · " + m.hojas + " hojas · profundidad real " + m.profundidad));

        if (!arbol.hoja) {
          info.appendChild(crearElemento("p", "lab-nota",
            "Primera división (raíz): " + ETIQUETAS[arbol.variable] + " ≤ " + formatearNumero(arbol.umbral) +
            ". Impureza " + etiquetaCriterio + " antes: " + formatearNumero(arbol.impureza) +
            " → después (ponderada): " + formatearNumero(arbol.ponderada) +
            ". Ganancia: " + formatearNumero(arbol.ganancia) + "."));
        }

        // Matriz de confusión sobre los datos de prueba (positivo = aprueba)
        const mc = test.matriz;
        info.appendChild(crearElemento("p", "", "Matriz de confusión (datos de prueba):"));
        info.appendChild(tablaSimple(
          ["", "Predice: Aprueba", "Predice: No aprueba"],
          [
            ["Real: Aprueba", mc[0][0] + " (verdaderos positivos)", mc[0][1] + " (falsos negativos)"],
            ["Real: No aprueba", mc[1][0] + " (falsos positivos)", mc[1][1] + " (verdaderos negativos)"],
          ]
        ));
        const predichosPositivos = mc[0][0] + mc[1][0];
        const realesPositivos = mc[0][0] + mc[0][1];
        info.appendChild(crearElemento("p", "lab-nota",
          "Precisión: " + (predichosPositivos ? porcentaje(mc[0][0] / predichosPositivos) : "—") +
          " (de los que predice que aprueban, cuántos aprueban de verdad) · Sensibilidad: " +
          (realesPositivos ? porcentaje(mc[0][0] / realesPositivos) : "—") +
          " (de los que aprueban, cuántos detecta)."));

        // Reglas del árbol (si no son demasiadas)
        if (m.hojas <= 8) {
          const lista = [];
          reglas(arbol, [], lista);
          info.appendChild(crearElemento("p", "", "Reglas del árbol:"));
          const ul = document.createElement("ul");
          for (const r of lista) ul.appendChild(crearElemento("li", "lab-nota", r));
          info.appendChild(ul);
        } else {
          info.appendChild(crearElemento("p", "lab-nota",
            "El árbol tiene " + m.hojas + " hojas: demasiadas reglas para listarlas. Compara la exactitud de " +
            "entrenamiento con la de prueba."));
        }

        info.appendChild(crearLeyenda([
          { color: COLORES[0], texto: NOMBRES[0] },
          { color: COLORES[1], texto: NOMBRES[1] },
        ]));
        info.appendChild(crearElemento("p", "lab-nota",
          "Círculos = estudiantes de entrenamiento (con ellos se construye el árbol). Cuadrados = estudiantes de " +
          "prueba (el árbol nunca los vio). Las líneas punteadas son las divisiones del árbol."));
      }

      dibujar();
    },
  };
})();
