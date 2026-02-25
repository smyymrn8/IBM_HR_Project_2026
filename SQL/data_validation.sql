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

-- Gruplanabilecek kategorik sütunların benzersiz değerlerini kontrol etme: BusinessTravel, Department, EducationField, Gender, JobRole, MaritalStatus
-- Bu sorgular, her bir kategorik sütunun benzersiz değerlerini listeleyecektir, böylece veri temizliği ve analiz için hangi kategorilerin mevcut olduğunu görebiliriz ve gerektiğinde bu kategorileri gruplandırabiliriz.
-- Aynı zamanda bu sorgular, verilerin doğruluğunu ve tutarlılığını kontrol etmek için de kullanılabilir, çünkü beklenmeyen veya hatalı kategorik değerler veri kalitesini etkileyebilir.
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
-- Analiz aşamasında bu sütunların tek bir değere sahip olduğunu görürsek, bu sütunların analizde kullanılmayabileceğini düşünebiliriz, çünkü değişkenlik göstermeyen sütunlar genellikle modelleme ve analiz için faydalı değildir.
SELECT DISTINCT EmployeeCount, Over18, StandardHours
FROM Employees
GO

-- Veri doğrulama için bir görünüm(view) oluşturma: vw_Data_QualityCheck
-- Bu view, Employees tablosundaki verilerin kalitesini değerlendirmek için çeşitli doğrulama kontrolleri içerir.
CREATE OR ALTER VIEW vw_Data_QualityCheck AS
SELECT 
    *,
    -- EmployeeNumber için veri doğrulama: Eksik veya tekrar eden değerleri kontrol etme
    CASE 
        WHEN EmployeeNumber IS NULL THEN 'Missing EmployeeNumber'
        WHEN EmployeeNumber IN (SELECT EmployeeNumber FROM Employees GROUP BY EmployeeNumber HAVING COUNT(*) > 1) THEN 'Duplicate EmployeeNumber'
        ELSE 'Valid EmployeeNumber'
    END AS EmployeeNumber_Validation,

    -- NullError kontrolü: Tüm sütunlarda NULL değerlerin olup olmadığını kontrol etme
    CASE WHEN
        Age IS NULL OR
        Attrition IS NULL OR
        BusinessTravel IS NULL OR
        DailyRate IS NULL OR
        Department IS NULL OR
        DistanceFromHome IS NULL OR
        Education IS NULL OR
        EducationField IS NULL OR
        EmployeeCount IS NULL OR
        EnvironmentSatisfaction IS NULL OR
        Gender IS NULL OR
        HourlyRate IS NULL OR
        JobInvolvement IS NULL OR
        JobLevel IS NULL OR
        JobRole IS NULL OR
        JobSatisfaction IS NULL OR
        MaritalStatus IS NULL OR
        MonthlyIncome IS NULL OR
        MonthlyRate IS NULL OR
        NumCompaniesWorked IS NULL OR
        Over18 IS NULL OR
        OverTime IS NULL OR
        PercentSalaryHike IS NULL OR
        PerformanceRating IS NULL OR
        RelationshipSatisfaction IS NULL OR
        StandardHours IS NULL OR
        StockOptionLevel IS NULL OR
        TotalWorkingYears IS NULL OR
        TrainingTimesLastYear IS NULL OR
        WorkLifeBalance IS NULL OR
        YearsAtCompany IS NULL OR
        YearsInCurrentRole IS NULL OR
        YearsSinceLastPromotion IS NULL OR
        YearsWithCurrManager IS NULL
    THEN 1 ELSE 0 END AS NullError,

    -- ValueError kontrolü: Sayısal sütunlarda mantıksal olarak mümkün olmayan değerleri kontrol etme
    CASE WHEN
        Age < 18 OR
        DailyRate <= 0 OR
        DistanceFromHome < 0 OR
        HourlyRate <= 0 OR
        MonthlyIncome <= 0 OR
        MonthlyRate <= 0 OR
        NumCompaniesWorked < 0 OR
        PercentSalaryHike < 0 OR
        TotalWorkingYears < 0 OR
        TrainingTimesLastYear < 0 OR
        YearsAtCompany < 0 OR
        YearsInCurrentRole < 0 OR
        YearsSinceLastPromotion < 0 OR
        YearsWithCurrManager < 0 OR
        Education NOT BETWEEN 1 AND 5 OR
        EnvironmentSatisfaction NOT BETWEEN 1 AND 4 OR
        JobInvolvement NOT BETWEEN 1 AND 4 OR
        JobLevel NOT BETWEEN 1 AND 5 OR
        JobSatisfaction NOT BETWEEN 1 AND 4 OR
        PerformanceRating NOT BETWEEN 1 AND 4 OR
        RelationshipSatisfaction NOT BETWEEN 1 AND 4 OR
        StockOptionLevel NOT BETWEEN 0 AND 3 OR
        WorkLifeBalance NOT BETWEEN 1 AND 4
    THEN 1 ELSE 0 END AS ValueError,

    -- LogicError kontrolü: Birbirleriyle mantıksal olarak tutarsız olan sütun değerlerini kontrol etme
    CASE WHEN
        YearsAtCompany > TotalWorkingYears OR
        YearsInCurrentRole > YearsAtCompany OR
        YearsWithCurrManager > YearsAtCompany OR
        YearsInCurrentRole > TotalWorkingYears OR
        YearsWithCurrManager > TotalWorkingYears
    THEN 1 ELSE 0 END AS LogicError,

    -- Attrition kontrolü (Yes veya No olmalı)
    CASE 
        WHEN Attrition NOT IN ('Yes','No') THEN 'Invalid Attrition'
        ELSE 'Valid Attrition'
    END AS Attrition_Validation,

    -- EmployeeCount kontrolü (sabit 1 olmalı)
    CASE 
        WHEN EmployeeCount != 1 THEN 'Invalid EmployeeCount'
        ELSE 'Valid EmployeeCount'
    END AS EmployeeCount_Validation,

    -- Gender kontrolü (Male veya Female olmalı)
    CASE 
        WHEN Gender NOT IN ('Male','Female') THEN 'Invalid Gender'
        ELSE 'Valid Gender'
    END AS Gender_Validation,

    -- Over18 kontrolü (sabit 'Y' olmalı)
    CASE 
        WHEN Over18 != 'Y' THEN 'Invalid Over18'
        ELSE 'Valid Over18'
    END AS Over18_Validation,

    -- OverTime kontrolü (Yes veya No olmalı) 
    CASE 
        WHEN OverTime NOT IN ('Yes','No') THEN 'Invalid OverTime'
        ELSE 'Valid OverTime'
    END AS OverTime_Validation,

    -- StandartHours kontrolü (sabit 80 olmalı)
    CASE
        WHEN StandardHours != 80 THEN 'Invalid StandartHours'
        ELSE 'Valid StandartHours'
    END AS StandartHours_Validation

FROM Employees;
GO


-- Kontrol edelim: vw_Data_QualityCheck view'da kaç tane NullError, ValueError veya LogicError olduğunu sayma
SELECT COUNT(*) 
FROM vw_Data_QualityCheck
WHERE NullError = 1
    OR ValueError = 1
    OR LogicError = 1;

