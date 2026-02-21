USE IBM_HR_DB;
GO

-- Explore all objects in the datebase to understand the structure of the IBM_HR_DB database
SELECT * FROM INFORMATION_SCHEMA.TABLES

-- Explore all columns in the database to understand the structure of the Employees table
SELECT * FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Employees'

