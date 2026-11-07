// Laboratorio: agrupamiento con K-means, paso a paso.
(function () {
  // ---- Algoritmo ----
  function asignarPuntos(puntos, centroides) {
    return puntos.map((p) => {
      let mejor = 0;
      let menor = Infinity;
      centroides.forEach((c, j) => {
        const d = distancia2(p, c);
        if (d < menor) { menor = d; mejor = j; }
      });
      return mejor;
    });
  }

  function moverCentroides(puntos, asign, centroides) {
    return centroides.map((c, j) => {
      let sx = 0, sy = 0, n = 0;
      puntos.forEach((p, i) => {
        if (asign[i] === j) { sx += p[0]; sy += p[1]; n++; }
      });
      return n ? [sx / n, sy / n] : c;   // un grupo vacío conserva su centroide
    });
  }

  function inercia(puntos, asign, centroides) {
    let total = 0;
    puntos.forEach((p, i) => { total += distancia2(p, centroides[asign[i]]); });
    return total;
  }

  function elegirAlAzar(puntos, k, azar) {
    const idx = puntos.map((_, i) => i);
    for (let i = idx.length - 1; i > 0; i--) {
      const j = Math.floor(azar() * (i + 1));
      const t = idx[i]; idx[i] = idx[j]; idx[j] = t;
    }
    return idx.slice(0, k).map((i) => puntos[i].slice());
  }

  // K-means completo con varios reinicios; devuelve la mejor (menor) inercia
  function mejorInercia(puntos, k, azar) {
    let mejor = Infinity;
    for (let intento = 0; intento < 15; intento++) {
      let cent = elegirAlAzar(puntos, k, azar);
      let asig = null;
      for (let it = 0; it < 100; it++) {
        const nueva = asignarPuntos(puntos, cent);
        if (asig && nueva.every((v, i) => v === asig[i])) break;
        asig = nueva;
        cent = moverCentroides(puntos, asig, cent);
      }
      mejor = Math.min(mejor, inercia(puntos, asig, cent));
    }
    return mejor;
  }

  LABS.kmeans = {
    montar(contenedor) {
      // ---- Datos: 3 grupos naturales de 30 puntos en un plano de 0 a 100 ----
      const azar = generadorAleatorio(3);
      const originales = [];
      for (const c of [[25, 25], [72, 30], [45, 76]]) {
        for (let i = 0; i < 30; i++) {
          originales.push([
            limitar(normalAleatoria(azar, c[0], 7), 0, 100),
            limitar(normalAleatoria(azar, c[1], 7), 0, 100),
          ]);
        }
      }
      let puntos = originales.map((p) => p.slice());

      const ex = crearEscala([0, 100], [AREA.x, AREA.x + AREA.w]);
      const ey = crearEscala([0, 100], [AREA.y + AREA.h, AREA.y]);

      // ---- Estado ----
      let k = 3;
      let centroides = [];
      let asign = null;          // null = todavía no se han asignado los puntos
      let fase = "asignar";      // lo que hará el siguiente paso: "asignar" o "actualizar"
      let iteracion = 0;
      let convergido = false;
      let temporizador = null;
      let codo = [];             // inercia mínima para k = 1..8

      // ---- Interfaz ----
      const controles = crearElemento("div", "lab-controles");
      controles.appendChild(crearDeslizador("k (número de grupos)", 1, 6, 1, k, (v) => { k = v; reiniciar(); }));
      const botonPaso = crearBoton("", () => { detener(); paso(); }, "lab-boton principal");
      const botonTodo = crearBoton("Ejecutar hasta converger", () => ejecutarTodo());
      controles.appendChild(botonPaso);
      controles.appendChild(botonTodo);
      controles.appendChild(crearBoton("Reiniciar centroides", () => reiniciar()));
      controles.appendChild(crearBoton("Restaurar datos", () => {
        puntos = originales.map((p) => p.slice());
        actualizarCodo();
        reiniciar();
      }));

      const lienzo = crearLienzo(600, 360);
      const info = crearElemento("div", "lab-info");
      const cajaCodo = crearElemento("div", "lab-info");
      contenedor.appendChild(controles);
      contenedor.appendChild(lienzo.canvas);
      contenedor.appendChild(info);
      contenedor.appendChild(cajaCodo);

      // ---- Control del algoritmo ----
      function detener() {
        if (temporizador) { clearInterval(temporizador); temporizador = null; }
      }

      function reiniciar() {
        detener();
        centroides = elegirAlAzar(puntos, k, Math.random);
        asign = null;
        fase = "asignar";
        iteracion = 0;
        convergido = false;
        dibujar();
      }

      function paso() {
        if (convergido) return;
        if (fase === "asignar") {
          const nueva = asignarPuntos(puntos, centroides);
          const igual = asign !== null && nueva.every((v, i) => v === asign[i]);
          asign = nueva;
          if (igual) { convergido = true; detener(); } else { fase = "actualizar"; }
        } else {
          centroides = moverCentroides(puntos, asign, centroides);
          iteracion++;
          fase = "asignar";
        }
        dibujar();
      }

      function ejecutarTodo() {
        detener();
        if (convergido) return;
        temporizador = setInterval(paso, 450);
      }

      function actualizarCodo() {
        const generador = generadorAleatorio(99);
        codo = [];
        for (let kk = 1; kk <= 8; kk++) codo.push(mejorInercia(puntos, kk, generador));
      }

      // ---- Dibujo ----
      function dibujar() {
        const ctx = lienzo.ctx;
        ctx.clearRect(0, 0, lienzo.ancho, lienzo.alto);
        dibujarEjes(ctx, ex, ey, "Variable 1", "Variable 2");

        // Líneas finas de cada punto a su centroide
        if (asign) {
          ctx.lineWidth = 1;
          puntos.forEach((p, i) => {
            const c = centroides[asign[i]];
            ctx.strokeStyle = PALETA[asign[i]] + "40";
            ctx.beginPath(); ctx.moveTo(ex(p[0]), ey(p[1])); ctx.lineTo(ex(c[0]), ey(c[1])); ctx.stroke();
          });
        }
        // Puntos (grises hasta que se asignan)
        puntos.forEach((p, i) => {
          dibujarCirculo(ctx, ex(p[0]), ey(p[1]), 4.5, asign ? PALETA[asign[i]] : "#9aa5b1", "#ffffff", 1);
        });
        // Centroides
        centroides.forEach((c, j) => {
          ctx.fillStyle = PALETA[j];
          ctx.strokeStyle = "#222222";
          ctx.lineWidth = 2.5;
          ctx.fillRect(ex(c[0]) - 7, ey(c[1]) - 7, 14, 14);
          ctx.strokeRect(ex(c[0]) - 7, ey(c[1]) - 7, 14, 14);
        });

        // ---- Botones y panel de información ----
        botonPaso.textContent = fase === "asignar" ? "Siguiente: asignar puntos" : "Siguiente: mover centroides";
        botonPaso.disabled = convergido;
        botonTodo.disabled = convergido;

        info.innerHTML = "";
        let linea = "Iteración " + iteracion + " · " + puntos.length + " puntos";
        if (asign) linea += " · Inercia: " + formatearNumero(inercia(puntos, asign, centroides));
        info.appendChild(crearElemento("p", "", linea));
        info.appendChild(crearElemento("p", "lab-nota", convergido
          ? "✓ Convergió: al asignar de nuevo ningún punto cambió de grupo, así que los centroides ya no se mueven."
          : "Los cuadrados son los centroides. Haz clic en el gráfico para añadir puntos. " +
            "Inercia = suma de las distancias al cuadrado de cada punto a su centroide."));

        // Curva del codo
        cajaCodo.innerHTML = "";
        cajaCodo.appendChild(crearElemento("p", "", "Curva del codo: mejor inercia que se encuentra para cada k"));
        const maximo = Math.max(...codo);
        codo.forEach((valor, i) => {
          const fila = crearElemento("div", "lab-fila-barra" + (i + 1 === k ? " actual" : ""));
          fila.appendChild(crearElemento("span", "etiqueta", "k=" + (i + 1)));
          const pista = crearElemento("div", "pista");
          const relleno = crearElemento("div", "relleno");
          relleno.style.width = (100 * valor) / maximo + "%";
          pista.appendChild(relleno);
          fila.appendChild(pista);
          fila.appendChild(crearElemento("span", "valor", formatearNumero(valor)));
          cajaCodo.appendChild(fila);
        });
      }

      // Clic: añadir un punto nuevo
      lienzo.canvas.addEventListener("click", (evento) => {
        const pos = posicionEnLienzo(evento, lienzo);
        const x = ex.inversa(pos.x);
        const y = ey.inversa(pos.y);
        if (x < 0 || x > 100 || y < 0 || y > 100) return;
        puntos.push([x, y]);
        actualizarCodo();
        asign = null;
        fase = "asignar";
        iteracion = 0;
        convergido = false;
        detener();
        dibujar();
      });

      actualizarCodo();
      reiniciar();
    },
  };
})();
