CREATE DATABASE IF NOT EXISTS quotes;
CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'ADMINadmin123';
GRANT ALL PRIVILEGES ON `quotes`.* TO 'admin'@'localhost';
GRANT SELECT ON `performance_schema`.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;