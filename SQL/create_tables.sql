-- create_tables.sql
-- Dataset'e uygun tablo oluşturma
USE IBM_HR_DB;
GO

CREATE TABLE Employees (
    EmployeeID INT IDENTITY(1,1) PRIMARY KEY,
    Age INT,
    Attrition NVARCHAR(10),
    BusinessTravel NVARCHAR(50),
    Department NVARCHAR(50),
    Education INT,
    EducationField NVARCHAR(50),
    EnvironmentSatisfaction INT,
    Gender NVARCHAR(10),
    JobInvolvement INT,
    JobLevel INT,
    JobRole NVARCHAR(50),
    JobSatisfaction INT,
    MaritalStatus NVARCHAR(20),
    MonthlyIncome INT,
    NumCompaniesWorked INT,
    OverTime NVARCHAR(10),
    PercentSalaryHike INT,
    PerformanceRating INT,
    RelationshipSatisfaction INT,
    StockOptionLevel INT,
    TotalWorkingYears INT,
    TrainingTimesLastYear INT,
    WorkLifeBalance INT,
    YearsAtCompany INT,
    YearsInCurrentRole INT,
    YearsSinceLastPromotion INT,
    YearsWithCurrManager INT
);
GO
