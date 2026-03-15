USE IBM_HR_DB;
GO

-- Feature engineering için bir görünüm(view) oluşturma: vw_HR_Feature_Engineering
-- Bu view, Employees tablosundaki verilerden yeni özellikler (features) türetmek için çeşitli hesaplamalar ve kategorik dönüşümler içerir.
CREATE VIEW vw_HR_Feature_Engineering AS
SELECT
    *,
    
    -- Salary fairness 
    MonthlyIncome * 1.0 / JobLevel AS income_per_level,

    -- Salary gap
    MonthlyIncome - AVG(MonthlyIncome) OVER (PARTITION BY JobLevel) AS salary_gap,

    -- Career stability
    YearsAtCompany * 1.0 / NULLIF(TotalWorkingYears,0) AS tenure_ratio,

    -- Promotion stagnation
    YearsSinceLastPromotion * 1.0 / NULLIF(YearsAtCompany,0) AS promotion_delay,

    -- Satisfaction index
    (
        JobSatisfaction +
        EnvironmentSatisfaction +
        WorkLifeBalance +
        RelationshipSatisfaction
    ) / 4.0 AS satisfaction_index,

    -- Income vs experience
    MonthlyIncome * 1.0 / NULLIF(TotalWorkingYears,0) AS income_per_experience,

    -- Commute stress
    DistanceFromHome * 1.0 / NULLIF(Age,0) AS commute_ratio,

    -- Age group 
    CASE
        WHEN Age < 30 THEN 'Young'
        WHEN Age BETWEEN 30 AND 40 THEN 'Mid Age'
        ELSE 'Senior'
    END AS Age_Group,

    -- Income levels
    CASE
        WHEN MonthlyIncome < 3000 THEN 'Low Income'
        WHEN MonthlyIncome BETWEEN 3000 AND 7000 THEN 'Medium Income'
        ELSE 'High Income'
    END AS Income_Level,

    -- Tenure groups (Company Experience)
    CASE
        WHEN YearsAtCompany < 2 THEN 'New Employee'
        WHEN YearsAtCompany BETWEEN 2 AND 5 THEN 'Junior'
        WHEN YearsAtCompany BETWEEN 6 AND 10 THEN 'Mid Tenure'
        ELSE 'Long Tenure'
    END AS Tenure_Group,

    -- Career stage
    CASE
        WHEN Age < 30 AND YearsAtCompany < 3 THEN 'Early Career'
        WHEN Age BETWEEN 30 AND 40 THEN 'Mid Career'
        ELSE 'Senior Career'
    END AS Career_Stage

FROM Employees;
GO



-- Kontrol sorgusu
SELECT 
    Age_Group,
    COUNT(*) AS EmployeeCount
FROM vw_HR_Feature_Engineering
GROUP BY Age_Group

ORDER BY EmployeeCount DESC;
