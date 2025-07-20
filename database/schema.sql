
/*
    * Swiftmmate 1.0.0
    * Database schema for Swiftmate
    * This file defines the structure of the users table used for authentication.
    * It includes fields for user ID, email, access token, refresh token, token expiry, and scopes.
    * 
    * Note: Ensure to replace the connection details in the .env file with your actual database credentials.
    *
*/

-- SQL script to create the users table for Swiftmate authentication
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    access_token VARCHAR(1024) NOT NULL,
    refresh_token VARCHAR(1024),
    token_expiry DATETIME,
    scopes VARCHAR(512)
);