// Laboratorio: normalización de datos (Min-Max y Z-score).
(function () {
  LABS.normalizacion = {
    montar(contenedor) {
      // ---- Datos: 40 personas con edad (años) y salario (miles de pesos) ----
      const azar = generadorAleatorio(11);
      const personas = [];
      for (let i = 0; i < 40; i++) {
        const edad = Math.round(limitar(normalAleatoria(azar, 36, 10), 18, 60));
        const salario = Math.max(1200, Math.round(1500 + (edad - 18) * 110 + normalAleatoria(azar, 0, 700)));
        personas.push([edad, salario]);
      }
      const ATIPICO = [40, 30000];
      let iA = personas.findIndex((p) => p[0] <= 26);
      let iB = personas.findIndex((p) => p[0] >= 50);
      if (iA < 0) iA = 0;
      if (iB < 0) iB = 1;

      let metodo = "original";
      let conAtipico = false;

      // ---- Interfaz ----
      const controles = crearElemento("div", "lab-controles");
      controles.appendChild(
        crearSelector(
          [
            { id: "original", texto: "Sin normalizar" },
            { id: "minmax", texto: "Min-Max [0, 1]" },
            { id: "zscore", texto: "Z-score" },
          ],
          metodo,
          (id) => { metodo = id; dibujar(); }
        )
      );
      const botonAtipico = crearBoton("Añadir valor atípico", () => {
        conAtipico = !conAtipico;
        botonAtipico.classList.toggle("activo", conAtipico);
        botonAtipico.textContent = conAtipico ? "Quitar valor atípico" : "Añadir valor atípico";
        dibujar();
      });
      controles.appendChild(botonAtipico);

      const lienzo = crearLienzo(600, 360);
      const info = crearElemento("div", "lab-info");
      contenedor.appendChild(controles);
      contenedor.appendChild(lienzo.canvas);
      contenedor.appendChild(info);

      // ---- Cálculo ----
      function transformar(datos) {
        if (metodo === "original") return datos.map((p) => [p[0], p[1]]);
        const est = [0, 1].map((j) => estadisticas(datos.map((p) => p[j])));
        return datos.map((p) =>
          p.map((v, j) =>
            metodo === "minmax"
              ? (v - est[j].min) / (est[j].max - est[j].min)
              : (v - est[j].media) / est[j].desv
          )
        );
      }

      function dibujar() {
        const crudos = conAtipico ? personas.concat([ATIPICO]) : personas;
        const datos = transformar(crudos);
        const xs = datos.map((p) => p[0]);
        const ys = datos.map((p) => p[1]);
        const ex = crearEscala(ampliar(Math.min(...xs), Math.max(...xs)), [AREA.x, AREA.x + AREA.w]);
        const ey = crearEscala(ampliar(Math.min(...ys), Math.max(...ys)), [AREA.y + AREA.h, AREA.y]);

        const ctx = lienzo.ctx;
        ctx.clearRect(0, 0, lienzo.ancho, lienzo.alto);
        const sufijo = metodo === "original" ? "" : " (normalizado)";
        dibujarEjes(ctx, ex, ey,
          metodo === "original" ? "Edad (años)" : "Edad" + sufijo,
          metodo === "original" ? "Salario (miles de $)" : "Salario" + sufijo);

        // Recta entre A y B
        const A = datos[iA], B = datos[iB];
        ctx.save();
        ctx.setLineDash([6, 5]);
        ctx.strokeStyle = "#999999";
        ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.moveTo(ex(A[0]), ey(A[1])); ctx.lineTo(ex(B[0]), ey(B[1])); ctx.stroke();
        ctx.restore();

        // Puntos
        datos.forEach((p, i) => {
          if (i === iA || i === iB) return;
          const esAtipico = conAtipico && i === crudos.length - 1;
          dibujarCirculo(ctx, ex(p[0]), ey(p[1]), esAtipico ? 7 : 5,
            esAtipico ? "#ff4b4b" : "#1cb0f6", "#ffffff", 1.5);
        });
        [[iA, "A", "#ff9600"], [iB, "B", "#a560e8"]].forEach(([i, letra, color]) => {
          dibujarCirculo(ctx, ex(datos[i][0]), ey(datos[i][1]), 8, color, "#ffffff", 2);
          ctx.fillStyle = "#333333";
          ctx.font = "bold 13px 'Segoe UI', Arial, sans-serif";
          ctx.textAlign = "left"; ctx.textBaseline = "bottom";
          ctx.fillText(letra, ex(datos[i][0]) + 10, ey(datos[i][1]) - 6);
        });

        // ---- Panel de información ----
        const filas = [["Edad", 0], ["Salario", 1]].map(([nombre, j]) => {
          const e = estadisticas(datos.map((p) => p[j]));
          return [nombre, formatearNumero(e.min), formatearNumero(e.max),
                  formatearNumero(e.media), formatearNumero(e.desv)];
        });

        const dx2 = (A[0] - B[0]) * (A[0] - B[0]);
        const dy2 = (A[1] - B[1]) * (A[1] - B[1]);
        const total = dx2 + dy2 || 1;
        const pctEdad = Math.round((100 * dx2) / total);
        const pctSalario = 100 - pctEdad;

        info.innerHTML = "";
        info.appendChild(tablaSimple(["Variable", "Mínimo", "Máximo", "Media", "Desv. est."], filas));
        info.appendChild(crearElemento("p", "",
          "Distancia entre A y B: " + formatearNumero(Math.sqrt(dx2 + dy2)) +
          " · aporte de la edad: " + pctEdad + " % · aporte del salario: " + pctSalario + " %"));
        const barra = crearElemento("div", "lab-apilada");
        const parteA = crearElemento("span", "parte-a");
        parteA.style.width = pctEdad + "%";
        const parteB = crearElemento("span", "parte-b");
        parteB.style.width = pctSalario + "%";
        barra.appendChild(parteA);
        barra.appendChild(parteB);
        info.appendChild(barra);
        info.appendChild(crearLeyenda([
          { color: "#1cb0f6", texto: "Edad" },
          { color: "#ff9600", texto: "Salario" },
        ]));
      }

      dibujar();
    },
  };
})();
