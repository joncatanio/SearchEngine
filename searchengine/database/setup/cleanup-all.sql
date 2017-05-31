-- Navigate to the proper DB
use SearchEngineDB;

-- Drop all tables avoiding FK issues
DROP TABLE IF EXISTS Hyperlinks;
DROP TABLE IF EXISTS WordMeta;
DROP TABLE IF EXISTS Links;
DROP TABLE IF EXISTS Words;

-- Drop the database entirely
DROP DATABASE IF EXISTS SearchEngineDB;

-- Finally, drop the user
DROP USER IF EXISTS 'searchEngineUser'@'localhost';
