-- SQL script for data validation in the IBM_HR_DB database
-- This script explores the structure of the database, checks for duplicates in the EmployeeNumber column, and examines the unique values in categorical columns.

USE IBM_HR_DB;
GO

-- Explore all objects in the datebase to understand the structure of the IBM_HR_DB database
SELECT * FROM INFORMATION_SCHEMA.TABLES

-- Explore all columns in the database to understand the structure of the Employees table
SELECT * FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Employees'

-- Total number of employees in the Employees table
SELECT COUNT(*) AS Total_Employees 
FROM Employees

-- Total number of columns in the Employees table
SELECT COUNT(*) AS Total_Columns 
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Employees'

-- Primary key control: Check if EmployeeID is unique and not null
SELECT EmployeeNumber, COUNT(*) AS Occurrences
FROM Employees
GROUP BY EmployeeNumber
HAVING COUNT(*) > 1 OR EmployeeNumber IS NULL

-- Gruplanabilecek kategorik sütunların benzersiz değerlerini kontrol etme: BusinessTravel, Department, EducationField, Gender, JobRole, MaritalStatus
-- Bu sorgular, her bir kategorik sütunun benzersiz değerlerini listeleyecektir, böylece veri temizliği ve analiz için hangi kategorilerin mevcut olduğunu görebiliriz ve gerektiğinde bu kategorileri gruplandırabiliriz.
SELECT DISTINCT BusinessTravel
FROM Employees

SELECT DISTINCT Department
FROM Employees

SELECT DISTINCT EducationField
FROM Employees

SELECT DISTINCT Gender
FROM Employees

SELECT DISTINCT JobRole
FROM Employees

SELECT DISTINCT MaritalStatus
FROM Employees

-- Sabit değer kontrolü: EmployeeCount, Over18, StandardHours sütunlarının tek bir değere sahip olup olmadığını kontrol etme
SELECT DISTINCT EmployeeCount, Over18, StandardHours
FROM Employees



