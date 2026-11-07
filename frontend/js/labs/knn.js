// Laboratorio: clasificación con k vecinos más cercanos (k-NN).
(function () {
  const NOMBRES = ["Aprueba", "No aprueba"];
  const COLORES = ["#58cc02", "#ff4b4b"];

  LABS.knn = {
    montar(contenedor) {
      // ---- Datos: 80 estudiantes (nota del parcial y asistencia, de 0 a 100) ----
      const azar = generadorAleatorio(21);
      const puntos = [];   // { x, y, clase }  clase 0 = aprueba, 1 = no aprueba
      for (let i = 0; i < 40; i++) {
        puntos.push({ x: limitar(normalAleatoria(azar, 66, 15), 2, 98), y: limitar(normalAleatoria(azar, 68, 15), 2, 98), clase: 0 });
      }
      for (let i = 0; i < 40; i++) {
        puntos.push({ x: limitar(normalAleatoria(azar, 34, 15), 2, 98), y: limitar(normalAleatoria(azar, 32, 15), 2, 98), clase: 1 });
      }

      const ex = crearEscala([0, 100], [AREA.x, AREA.x + AREA.w]);
      const ey = crearEscala([0, 100], [AREA.y + AREA.h, AREA.y]);
      const escalaX = AREA.w / 100;   // píxeles por unidad (para dibujar el radio)
      const escalaY = AREA.h / 100;

      let k = 3;
      let consulta = { x: 50, y: 50 };
      let mostrarFrontera = false;
      let cacheFrontera = null;       // { k, celdas } para no recalcular al arrastrar

      // ---- Cálculo ----
      function predecir(q, kk) {
        const vecinos = puntos
          .map((p, i) => ({ i, d: Math.sqrt(distancia2([p.x, p.y], [q.x, q.y])) }))
          .sort((a, b) => a.d - b.d)
          .slice(0, kk);
        const votos = [0, 0];
        vecinos.forEach((v) => { votos[puntos[v.i].clase]++; });
        const maximo = Math.max(votos[0], votos[1]);
        // En caso de empate gana la clase del vecino más cercano entre las empatadas
        const ganador = vecinos.find((v) => votos[puntos[v.i].clase] === maximo);
        return { vecinos, votos, clase: puntos[ganador.i].clase, empate: votos[0] === votos[1] };
      }

      function calcularFrontera() {
        if (cacheFrontera && cacheFrontera.k === k) return cacheFrontera.celdas;
        const columnas = 66, filas = 40, celdas = [];
        for (let f = 0; f < filas; f++) {
          for (let c = 0; c < columnas; c++) {
            const q = { x: ((c + 0.5) * 100) / columnas, y: ((f + 0.5) * 100) / filas };
            celdas.push(predecir(q, k).clase);
          }
        }
        cacheFrontera = { k, celdas, columnas, filas };
        return celdas;
      }

      // ---- Interfaz ----
      const controles = crearElemento("div", "lab-controles");
      controles.appendChild(crearDeslizador("k (vecinos)", 1, 25, 1, k, (v) => { k = v; dibujar(); }));
      const botonFrontera = crearBoton("Mostrar frontera de decisión", () => {
        mostrarFrontera = !mostrarFrontera;
        botonFrontera.classList.toggle("activo", mostrarFrontera);
        dibujar();
      });
      controles.appendChild(botonFrontera);

      const lienzo = crearLienzo(600, 360);
      const info = crearElemento("div", "lab-info");
      contenedor.appendChild(controles);
      contenedor.appendChild(lienzo.canvas);
      contenedor.appendChild(info);

      // ---- Dibujo ----
      function dibujar() {
        const ctx = lienzo.ctx;
        ctx.clearRect(0, 0, lienzo.ancho, lienzo.alto);
        dibujarEjes(ctx, ex, ey, "Nota del parcial", "Asistencia (%)");

        // Frontera de decisión: cada celda se pinta con la clase que se predeciría ahí
        if (mostrarFrontera) {
          const celdas = calcularFrontera();
          const { columnas, filas } = cacheFrontera;
          const ancho = AREA.w / columnas, alto = AREA.h / filas;
          celdas.forEach((clase, n) => {
            const c = n % columnas, f = Math.floor(n / columnas);
            ctx.fillStyle = COLORES[clase] + "26";
            ctx.fillRect(AREA.x + c * ancho, AREA.y + AREA.h - (f + 1) * alto, ancho + 0.5, alto + 0.5);
          });
        }

        const pred = predecir(consulta, k);
        const esVecino = new Set(pred.vecinos.map((v) => v.i));

        // Círculo (elipse en pantalla) hasta el vecino más lejano
        const radio = pred.vecinos[pred.vecinos.length - 1].d;
        ctx.save();
        ctx.setLineDash([6, 5]);
        ctx.strokeStyle = "#888888";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.ellipse(ex(consulta.x), ey(consulta.y), radio * escalaX, radio * escalaY, 0, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();

        // Líneas a los vecinos
        ctx.strokeStyle = "#55555588";
        ctx.lineWidth = 1.2;
        for (const v of pred.vecinos) {
          const p = puntos[v.i];
          ctx.beginPath(); ctx.moveTo(ex(consulta.x), ey(consulta.y)); ctx.lineTo(ex(p.x), ey(p.y)); ctx.stroke();
        }
        // Puntos
        puntos.forEach((p, i) => {
          dibujarCirculo(ctx, ex(p.x), ey(p.y), esVecino.has(i) ? 6 : 4.5, COLORES[p.clase],
            esVecino.has(i) ? "#222222" : "#ffffff", esVecino.has(i) ? 2.5 : 1);
        });
        // Punto nuevo: rombo del color de la clase predicha
        const cx = ex(consulta.x), cy = ey(consulta.y);
        ctx.beginPath();
        ctx.moveTo(cx, cy - 10); ctx.lineTo(cx + 10, cy); ctx.lineTo(cx, cy + 10); ctx.lineTo(cx - 10, cy);
        ctx.closePath();
        ctx.fillStyle = COLORES[pred.clase];
        ctx.fill();
        ctx.strokeStyle = "#222222";
        ctx.lineWidth = 3;
        ctx.stroke();

        // ---- Panel de información ----
        info.innerHTML = "";
        info.appendChild(crearElemento("p", "",
          "Con k = " + k + " vecinos votan: " + NOMBRES[0] + " " + pred.votos[0] +
          " · " + NOMBRES[1] + " " + pred.votos[1] + "  →  Predicción: " + NOMBRES[pred.clase]));
        if (pred.empate) {
          info.appendChild(crearElemento("p", "lab-nota",
            "Hay empate: gana la clase del vecino más cercano."));
        }
        info.appendChild(crearLeyenda([
          { color: COLORES[0], texto: NOMBRES[0] },
          { color: COLORES[1], texto: NOMBRES[1] },
        ]));
        info.appendChild(crearElemento("p", "lab-nota",
          "El rombo es el estudiante nuevo; los puntos con borde oscuro son sus k vecinos. " +
          "Haz clic o arrastra para moverlo."));
      }

      // Clic o arrastre: mover el punto nuevo
      let arrastrando = false;
      function mover(evento) {
        const pos = posicionEnLienzo(evento, lienzo);
        consulta = { x: limitar(ex.inversa(pos.x), 0, 100), y: limitar(ey.inversa(pos.y), 0, 100) };
        dibujar();
      }
      lienzo.canvas.addEventListener("pointerdown", (evento) => {
        arrastrando = true;
        lienzo.canvas.setPointerCapture(evento.pointerId);
        mover(evento);
      });
      lienzo.canvas.addEventListener("pointermove", (evento) => { if (arrastrando) mover(evento); });
      lienzo.canvas.addEventListener("pointerup", () => { arrastrando = false; });
      lienzo.canvas.addEventListener("pointercancel", () => { arrastrando = false; });

      dibujar();
    },
  };
})();
