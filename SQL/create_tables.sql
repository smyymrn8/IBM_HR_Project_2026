-- Dataset'e uygun tablo oluşturma
USE IBM_HR_DB;
GO

CREATE TABLE Employees (
    EmployeeNumber INT PRIMARY KEY,
    Age INT,
    Attrition NVARCHAR(10),
    BusinessTravel NVARCHAR(50),
    DailyRate INT,
    Department NVARCHAR(50),
    DistanceFromHome INT,
    Education INT,
    EducationField NVARCHAR(50),
    EmplooyeeCount INT,
    EnvironmentSatisfaction INT,
    Gender NVARCHAR(10),
    HourlyRate INT,
    JobInvolvement INT,
    JobLevel INT,
    JobRole NVARCHAR(50),
    JobSatisfaction INT,
    MaritalStatus NVARCHAR(20),
    MonthlyIncome INT,
    MonthlyRate INT,
    NumCompaniesWorked INT,
    Over18 NVARCHAR(10),
    OverTime NVARCHAR(10),
    PercentSalaryHike INT,
    PerformanceRating INT,
    RelationshipSatisfaction INT,
    StandartHours INT,
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
