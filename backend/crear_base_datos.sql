-- Ejecuta este script en MySQL Workbench (o con: mysql -u root -p < crear_base_datos.sql)
-- Las TABLAS las crea la aplicación sola (sembrar_datos.py / uvicorn); aquí solo
-- se crea la base de datos y el usuario. Cambia la clave y usa la misma en el archivo .env

CREATE DATABASE IF NOT EXISTS aprendizaje
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'app_aprendizaje'@'localhost' IDENTIFIED BY 'cambia_esta_clave';
GRANT ALL PRIVILEGES ON aprendizaje.* TO 'app_aprendizaje'@'localhost';
FLUSH PRIVILEGES;
