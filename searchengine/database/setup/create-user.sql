-- Creates a new user that can only access information from localhost
CREATE USER IF NOT EXISTS 'searchEngineUser'@'localhost'
   IDENTIFIED BY 'search_engine_pw';

-- Grant specific privileges
GRANT SELECT, UPDATE, INSERT, CREATE TEMPORARY TABLES, DROP
   ON SearchEngineDB.* TO 'searchEngineUser'@'localhost';

GRANT DROP ON SearchEngineDB.WordMeta TO 'searchEngineUser'@'localhost';
GRANT DROP ON SearchEngineDB.Hyperlinks TO 'searchEngineUser'@'localhost';
