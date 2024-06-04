-- Create the 'quotes' database if it doesn't already exist
CREATE DATABASE IF NOT EXISTS quotes;

-- Create the 'admin' user with the password 'ADMINadmin123'
CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'ADMINadmin123';

-- Grant all privileges on the 'quotes' database to the 'admin' user
GRANT ALL PRIVILEGES ON `quotes`.* TO 'admin'@'localhost';

-- Grant SELECT privilege on the 'performance_schema' database to the 'admin' user
GRANT SELECT ON `performance_schema`.* TO 'admin'@'localhost';

-- Flush the privileges to apply the changes
FLUSH PRIVILEGES;