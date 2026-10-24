# Aprendizaje: Minería de datos

Aplicación web de aprendizaje gamificada, al estilo Duolingo. Enseña **minería de datos y temas
relacionados** con lecciones cortas, ejercicios, puntos de experiencia, rachas diarias, logros y un
avatar (un robot) que se personaliza con monedas ganadas al estudiar.

## Resumen

El usuario crea una cuenta, completa lecciones de opción múltiple y va ganando recompensas:

| Función | Cómo funciona |
|---|---|
| **Cursos y lecciones** | Un curso con 3 lecciones de 4 ejercicios cada una (minería de datos) |
| **Progreso** | Cada lección terminada se guarda con su puntaje y fecha |
| **XP y niveles** | La primera vez que se completa una lección se gana su XP completa; las repeticiones dan el 30%. Cada 20 XP se sube de nivel |
| **Racha diaria** | Se suma un día por cada jornada en que se completa al menos una lección. Si se salta un día, vuelve a empezar |
| **Monedas** | 2 por respuesta correcta (30% al repetir) más la recompensa de cada logro |
| **Logros** | Primer paso, lección perfecta, nivel 2, 3 lecciones, 3 y 7 días de racha |
| **Avatar y tienda** | Robot dibujado con SVG. Colores, ropa y accesorios que se compran con monedas o se desbloquean por nivel |
| **Cuentas** | Registro e inicio de sesión (usuario o correo), perfil, contraseñas con bcrypt y sesión con JWT |

El servidor corrige las respuestas y calcula la XP, las monedas y los logros; el navegador nunca
recibe las respuestas correctas.

**Tecnologías:** Python 3.12 · FastAPI · SQLAlchemy · MySQL · JWT (PyJWT) · bcrypt ·
HTML, CSS y JavaScript sin frameworks.

---

## Requisitos

- **Python 3.11 o superior.** Se recomienda **3.12**. Con versiones muy nuevas (3.15, por ejemplo) algunos
  paquetes todavía no tienen versión precompilada y la instalación falla.
- **MySQL 8** (MySQL Server; MySQL Workbench es opcional pero cómodo).
- Un navegador moderno.

---

## Instalación y ejecución local (Windows)

Los comandos se escriben en una terminal (PowerShell, Anaconda Prompt o la terminal de VS Code).

### 1. Obtener el proyecto

```powershell
git clone https://github.com/TU_USUARIO/aprendizaje.git
cd aprendizaje
```

### 2. Crear la base de datos en MySQL

Abre `backend/crear_base_datos.sql` y **cambia la clave** `cambia_esta_clave` por una tuya. Luego ejecútalo
(te pedirá la clave del usuario `root` de MySQL):

```powershell
mysql -u root -p -e "source backend/crear_base_datos.sql"
```

También puedes abrir el archivo en MySQL Workbench y ejecutarlo. Crea la base de datos `aprendizaje` y el
usuario `app_aprendizaje`. Las tablas las crea la propia aplicación al arrancar.

### 3. Crear el entorno de Python e instalar las dependencias

Elige una de las dos opciones.

**Con Anaconda / Miniconda:**

```powershell
conda create -n aprendizaje python=3.12 -y
conda activate aprendizaje
cd backend
pip install -r requirements.txt
```

**Con venv (Python normal):**

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Si PowerShell dice que la ejecución de scripts está deshabilitada, ejecuta una vez
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a activar el entorno.

### 4. Configurar las variables de entorno

En la carpeta `backend`, copia el archivo de ejemplo y edítalo:

```powershell
copy .env.ejemplo .env
```

El archivo `.env` debe tener dos líneas:

```
URL_BASE_DATOS=mysql+pymysql://app_aprendizaje:TU_CLAVE@localhost:3306/aprendizaje
CLAVE_SECRETA=una_clave_larga_y_aleatoria
```

- La URL tiene el formato `mysql+pymysql://USUARIO:CLAVE@SERVIDOR:PUERTO/BASE_DE_DATOS`. Si la clave tiene
  símbolos, conviene codificarlos (`@` → `%40`, `#` → `%23`, `/` → `%2F`, `:` → `%3A`) o usar una clave solo
  con letras y números.
- Genera la `CLAVE_SECRETA` con este comando y pega el resultado:

  ```powershell
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

**El archivo `.env` es secreto: nunca se sube a GitHub** (ya está en `.gitignore`).

### 5. Cargar el contenido del curso

Solo la primera vez, desde `backend` con el entorno activado:

```powershell
python sembrar_datos.py
```

Debe responder: `Listo: curso, 3 lecciones y 12 ejercicios creados.`
(Con `python sembrar_datos.py --reiniciar` se borra toda la base de datos, usuarios incluidos, y se vuelve a empezar.)

### 6. Arrancar el servidor

```powershell
uvicorn app.main:app --reload
```

Abre **http://127.0.0.1:8000/**, crea una cuenta y empieza a estudiar.
Para detener el servidor, pulsa `Ctrl + C`.

Para volver a ejecutarlo otro día solo necesitas: activar el entorno, entrar a `backend` y repetir
el paso 6.

- Documentación interactiva de la API: http://127.0.0.1:8000/docs
- Los logros y los objetos de la tienda se cargan solos cada vez que arranca el servidor.

---

## Problemas frecuentes

| Síntoma | Causa y solución |
|---|---|
| `Microsoft Visual C++ 14.0 or greater is required` al instalar | Estás usando una versión de Python demasiado nueva. Crea un entorno con Python 3.12 |
| `Falta CLAVE_SECRETA en el archivo backend/.env` | Añade la línea `CLAVE_SECRETA=...` al `.env` |
| `Access denied` o `Can't connect to MySQL` | Revisa usuario, clave, puerto y nombre de la base en `URL_BASE_DATOS`, y que el servicio MySQL esté iniciado |
| `ModuleNotFoundError` | El entorno no está activado, o no estás en la carpeta `backend` |
| La página se queda en "Cargando..." tras actualizar archivos | El navegador usa archivos viejos guardados. Recarga con `Ctrl + F5` |
| La página no muestra lecciones | Falta ejecutar `python sembrar_datos.py` |

---

## Dónde cambiar cada cosa

| Quiero cambiar... | Archivo |
|---|---|
| Preguntas, lecciones o cursos | `backend/sembrar_datos.py` |
| XP por nivel, % de repetición, monedas por acierto | `backend/app/logica.py` |
| Logros | `backend/app/catalogo_logros.py` |
| Objetos de la tienda (precios y niveles) | `backend/app/catalogo_items.py` |
| Dibujo del robot, ropa y accesorios | `frontend/js/avatar.js` |
| Duración de la sesión | `backend/app/seguridad.py` (`MINUTOS_EXPIRACION`) |
| Estilos | `frontend/css/estilos.css` |

Si cambias un archivo `.js` o `.css`, sube el número de versión (`?v=5`) en los `.html` o recarga con `Ctrl + F5`.

---

## Estructura del proyecto

```
aprendizaje/
├── README.md
├── .gitignore
├── backend/
│   ├── app/
│   │   ├── main.py              arranca la aplicación
│   │   ├── base_datos.py        conexión a MySQL
│   │   ├── modelos.py           tablas de la base de datos
│   │   ├── esquemas.py          datos que entran y salen de la API
│   │   ├── logica.py            reglas del juego (XP, nivel, monedas, racha)
│   │   ├── seguridad.py         contraseñas (bcrypt) y tokens (JWT)
│   │   ├── dependencias.py      identifica al usuario a partir del token
│   │   ├── servicio_logros.py   evaluación de logros
│   │   ├── servicio_tienda.py   objetos del usuario y su avatar
│   │   ├── catalogo_logros.py   lista de logros
│   │   ├── catalogo_items.py    lista de objetos del avatar
│   │   └── rutas/               contenido, progreso, autenticación, logros, tienda, avatar
│   ├── sembrar_datos.py         carga el curso y los ejercicios
│   ├── crear_base_datos.sql     crea la base de datos y el usuario de MySQL
│   ├── requirements.txt         dependencias de Python
│   └── .env.ejemplo             modelo del archivo .env
└── frontend/
    ├── index.html  leccion.html  login.html  registro.html
    ├── perfil.html  logros.html  avatar.html
    ├── css/estilos.css
    └── js/                      un archivo por página, más api.js y avatar.js compartidos
```

El frontend lo sirve el propio FastAPI, así que no hace falta un segundo servidor.

---

## API principal

| Método y ruta | Qué hace | ¿Requiere sesión? |
|---|---|---|
| `POST /api/auth/registro` | Crea una cuenta y devuelve el token | No |
| `POST /api/auth/login` | Inicia sesión (usuario o correo) y devuelve el token | No |
| `GET /api/cursos`, `GET /api/cursos/{id}`, `GET /api/lecciones/{id}` | Contenido (sin respuestas correctas) | No |
| `POST /api/ejercicios/{id}/responder` | Corrige una respuesta | No |
| `GET /api/usuario/actual` | Perfil: XP, nivel, monedas y racha | Sí |
| `GET /api/progreso` | Lecciones completadas | Sí |
| `POST /api/lecciones/{id}/completar` | Guarda la lección y reparte XP, monedas, racha y logros | Sí |
| `GET /api/logros` | Logros y avance de cada uno | Sí |
| `GET /api/tienda`, `POST /api/tienda/comprar/{id}` | Ver y comprar objetos | Sí |
| `GET /api/avatar`, `PUT /api/avatar` | Ver y guardar el avatar | Sí |

Las rutas protegidas esperan la cabecera `Authorization: Bearer <token>`.

---

## Seguridad y límites actuales

- Las contraseñas se guardan con **bcrypt**; nunca en texto plano.
- La sesión usa un **token JWT** que dura 24 horas y el navegador lo guarda en `localStorage`.
- Es un proyecto de aprendizaje. Antes de publicarlo en internet habría que añadir HTTPS, límite de intentos
  de inicio de sesión, y guardar el token en una cookie `HttpOnly`.
- La racha usa la fecha del equipo donde corre el servidor; en un servidor de otra zona horaria habría que fijar la zona.
- Hoy todos los ejercicios son de opción múltiple. La estructura permite añadir más tipos (completar espacios, ordenar).

---

## Subir el proyecto a GitHub

1. Crea un repositorio vacío en GitHub (sin README, para no tener conflictos).
2. En la carpeta del proyecto:

   ```powershell
   git init
   git add .
   git status
   ```

   **Revisa la lista de `git status`: no debe aparecer `backend/.env`** (sí debe aparecer `backend/.env.ejemplo`).

3. Primer commit y subida:

   ```powershell
   git commit -m "Primera versión de la aplicación de aprendizaje"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/aprendizaje.git
   git push -u origin main
   ```

Si alguna vez subes el `.env` por error, cambia de inmediato la `CLAVE_SECRETA` y la clave de MySQL: quitar el archivo
del repositorio no borra su contenido del historial.
