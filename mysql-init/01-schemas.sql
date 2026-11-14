-- Um único servidor MySQL, um SCHEMA por microsserviço.
-- Cada serviço tem o seu usuário e só enxerga o próprio schema:
--   os_user      -> os_db
--   catalog_user -> catalog_db
--   billing_user -> billing_db
-- Roda só na PRIMEIRA subida (volume vazio). Para recriar: docker compose down -v

CREATE DATABASE IF NOT EXISTS os_db;
CREATE DATABASE IF NOT EXISTS catalog_db;
CREATE DATABASE IF NOT EXISTS billing_db;

CREATE USER IF NOT EXISTS 'os_user'@'%'      IDENTIFIED BY 'os_pass';
CREATE USER IF NOT EXISTS 'catalog_user'@'%' IDENTIFIED BY 'catalog_pass';
CREATE USER IF NOT EXISTS 'billing_user'@'%' IDENTIFIED BY 'billing_pass';

GRANT ALL PRIVILEGES ON os_db.*      TO 'os_user'@'%';
GRANT ALL PRIVILEGES ON catalog_db.* TO 'catalog_user'@'%';
GRANT ALL PRIVILEGES ON billing_db.* TO 'billing_user'@'%';

FLUSH PRIVILEGES;
