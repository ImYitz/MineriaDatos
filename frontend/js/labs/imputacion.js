// Laboratorio: valores faltantes (eliminar filas o imputar con media, mediana o vecinos).
(function () {
  LABS.imputacion = {
    montar(contenedor) {
      // ---- Datos: 60 viviendas con superficie (m²) y precio (millones) ----
      const azar = generadorAleatorio(5);
      const filas = [];
      for (let i = 0; i < 60; i++) {
        const x = Math.round(40 + 160 * azar());
        const y = Math.max(20, Math.round(40 + 1.9 * (x - 40) + normalAleatoria(azar, 0, 25)));
        filas.push({ x, y, u: azar() });     // u decide si el precio se "esconde"
      }
      const xsReales = filas.map((f) => f.x);
      const ysReales = filas.map((f) => f.y);
      const estReal = estadisticas(ysReales);
      const corrReal = correlacion(xsReales, ysReales);

      const ex = crearEscala(ampliar(Math.min(...xsReales), Math.max(...xsReales)), [AREA.x, AREA.x + AREA.w]);
      const ey = crearEscala(ampliar(0, Math.max(...ysReales)), [AREA.y + AREA.h, AREA.y]);

      let metodo = "eliminar";
      let porcentaje = 30;

      // ---- Interfaz ----
      const controles = crearElemento("div", "lab-controles");
      controles.appendChild(
        crearSelector(
          [
            { id: "eliminar", texto: "Eliminar filas" },
            { id: "media", texto: "Media" },
            { id: "mediana", texto: "Mediana" },
            { id: "vecinos", texto: "Vecinos (k = 3)" },
          ],
          metodo,
          (id) => { metodo = id; dibujar(); }
        )
      );
      controles.appendChild(
        crearDeslizador("Precios faltantes", 0, 60, 5, porcentaje, (v) => { porcentaje = v; dibujar(); }, " %")
      );

      const lienzo = crearLienzo(600, 360);
      const info = crearElemento("div", "lab-info");
      contenedor.appendChild(controles);
      contenedor.appendChild(lienzo.canvas);
      contenedor.appendChild(info);

      // ---- Cálculo ----
      function calcular() {
        const faltante = filas.map((f) => f.u < porcentaje / 100);
        const conocidos = filas.filter((f, i) => !faltante[i]);
        const yConocidos = conocidos.map((f) => f.y);
        const media = promedio(yConocidos);
        const mediana = estadisticas(yConocidos).mediana;

        function porVecinos(x) {
          const cercanos = conocidos
            .slice()
            .sort((a, b) => Math.abs(a.x - x) - Math.abs(b.x - x))
            .slice(0, 3);
          return promedio(cercanos.map((f) => f.y));
        }

        // usadas: filas con las que se trabaja después del método elegido
        const usadas = [];
        filas.forEach((f, i) => {
          if (!faltante[i]) {
            usadas.push({ x: f.x, y: f.y, imputado: false, real: f.y });
          } else if (metodo !== "eliminar") {
            const y = metodo === "media" ? media : metodo === "mediana" ? mediana : porVecinos(f.x);
            usadas.push({ x: f.x, y, imputado: true, real: f.y });
          }
        });
        return { usadas, faltante };
      }

      function dibujar() {
        const { usadas, faltante } = calcular();
        const ctx = lienzo.ctx;
        ctx.clearRect(0, 0, lienzo.ancho, lienzo.alto);
        dibujarEjes(ctx, ex, ey, "Superficie (m²)", "Precio (millones $)");

        // Valor real de lo que se escondió (gris claro)
        filas.forEach((f, i) => {
          if (faltante[i]) dibujarCirculo(ctx, ex(f.x), ey(f.y), 4.5, "#d9d9d9", "#bdbdbd", 1);
        });
        // Línea del valor inventado hasta el real, y el valor inventado (naranja)
        for (const u of usadas) {
          if (!u.imputado) continue;
          ctx.strokeStyle = "#ffc680";
          ctx.lineWidth = 1.5;
          ctx.beginPath(); ctx.moveTo(ex(u.x), ey(u.y)); ctx.lineTo(ex(u.x), ey(u.real)); ctx.stroke();
        }
        for (const u of usadas) {
          if (u.imputado) dibujarCirculo(ctx, ex(u.x), ey(u.y), 5.5, "#ff9600", "#ffffff", 1.5);
        }
        // Datos conocidos (azul)
        for (const u of usadas) {
          if (!u.imputado) dibujarCirculo(ctx, ex(u.x), ey(u.y), 5, "#1cb0f6", "#ffffff", 1.5);
        }

        // ---- Panel de información ----
        const est = estadisticas(usadas.map((u) => u.y));
        const corr = correlacion(usadas.map((u) => u.x), usadas.map((u) => u.y));
        const imputadas = usadas.filter((u) => u.imputado);
        const error = imputadas.length
          ? formatearNumero(promedio(imputadas.map((u) => Math.abs(u.y - u.real))))
          : "—";

        info.innerHTML = "";
        info.appendChild(tablaSimple(
          ["", "Filas", "Precio medio", "Desv. est.", "Correlación", "Error medio"],
          [
            ["Datos reales", filas.length, formatearNumero(estReal.media),
             formatearNumero(estReal.desv), formatearNumero(corrReal), "—"],
            ["Con el método", usadas.length, formatearNumero(est.media),
             formatearNumero(est.desv), formatearNumero(corr), error],
          ]
        ));
        info.appendChild(crearLeyenda([
          { color: "#1cb0f6", texto: "Dato conocido" },
          { color: "#ff9600", texto: "Valor imputado" },
          { color: "#d9d9d9", texto: "Valor real escondido" },
        ]));
        info.appendChild(crearElemento("p", "lab-nota",
          "Error medio = diferencia promedio entre el valor imputado y el real. " +
          "Compara también cómo cambian la desviación estándar y la correlación."));
      }

      dibujar();
    },
  };
})();
