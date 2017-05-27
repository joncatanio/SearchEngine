-- Creates a new user that can only access information from localhost
CREATE USER IF NOT EXISTS 'searchEngineUser'@'localhost'
   IDENTIFIED BY 'search_engine_pw';

-- Grant specific privileges
GRANT SELECT, UPDATE ON SearchEngineDB.* TO 'searchEngineUser'@'localhost';
