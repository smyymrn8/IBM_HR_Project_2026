
--yeni değişkenler üretirken tablo yapısı korunarak viewlar ile eklenebilir.
USE TBM_HR_DB;
GO

-- 6. haftada belirtilen yaş grupları, gelir seviyeleri ve kıdem süreleri sql sorguları ile sınıflandırılacak.
-- Bu sayede çalışanların ayrılmasını etkileyen faktörler daha iyi analiz edilebilir ve bu faktörlere göre stratejiler geliştirilebilir hale gelecek.

USE IBM_HR_DB;
GO

-- Feature Engineering View
-- Yaş grupları, gelir seviyeleri ve kıdem grupları oluşturuluyor

CREATE VIEW vw_HR_Feature_Engineering AS
SELECT
    *,
    
    -- Age Groups
    CASE
        WHEN Age < 25 THEN 'Young'
        WHEN Age BETWEEN 25 AND 34 THEN 'Early Career'
        WHEN Age BETWEEN 35 AND 44 THEN 'Mid Career'
        WHEN Age BETWEEN 45 AND 54 THEN 'Experienced'
        ELSE 'Senior'
    END AS Age_Group,

    -- Income Levels
    CASE
        WHEN MonthlyIncome < 3000 THEN 'Low Income'
        WHEN MonthlyIncome BETWEEN 3000 AND 7000 THEN 'Medium Income'
        ELSE 'High Income'
    END AS Income_Level,

    -- Tenure Groups (Company Experience)
    CASE
        WHEN YearsAtCompany < 2 THEN 'New Employee'
        WHEN YearsAtCompany BETWEEN 2 AND 5 THEN 'Junior'
        WHEN YearsAtCompany BETWEEN 6 AND 10 THEN 'Mid Tenure'
        ELSE 'Long Tenure'
    END AS Tenure_Group

FROM Employees;
GO

-- Kontrol sorgusu
SELECT 
    Age_Group,
    COUNT(*) AS EmployeeCount
FROM vw_HR_Feature_Engineering
GROUP BY Age_Group
ORDER BY EmployeeCount DESC;