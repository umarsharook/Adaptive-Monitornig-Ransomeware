-- Drop the table if it exists
DROP TABLE IF EXISTS `user`;

-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS ransomeware;

-- Switch to the created database
USE ransomeware;  -- This should be 'ransomeware' instead of 'dummy'

-- Create the user table
CREATE TABLE `user` (
    `name` VARCHAR(225),
    `email` VARCHAR(225),
    `password` VARCHAR(225),
    `conpass` VARCHAR(225),
    `number` VARCHAR(225)
);
