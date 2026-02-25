-- IBM_HR_DB veritabanında Employees tablosundaki kategorik sütunları daha anlaşılır hale getirmek için bir view oluşturuyoruz. 
-- Bu view, orijinal sütunların yanı sıra her kategorik sütun için etiketlenmiş bir sütun içerecektir.
-- Bu sayede, analiz yaparken kategorik değerlerin ne anlama geldiğini daha kolay anlayabiliriz.
-- Oluşturulan view, özellikle eğitim seviyesi, iş tatmini, performans değerlendirmesi gibi önemli kategorik sütunları etiketleyerek, veri analizi ve raporlama süreçlerini kolaylaştıracaktır.
-- Ayrıca, bu view sayesinde, kategorik sütunların değerlerini hatırlamak zorunda kalmadan, doğrudan etiketlenmiş sütunları kullanarak analiz yapabiliriz.

USE IBM_HR_DB;
GO

CREATE VIEW vw_HR_Attrition_Labeled AS
SELECT 
    *,
    -- Education
    CASE 
        WHEN Education = 1 THEN 'Below College'
        WHEN Education = 2 THEN 'College'
        WHEN Education = 3 THEN 'Bachelor'
        WHEN Education = 4 THEN 'Master'
        WHEN Education = 5 THEN 'Doctor'
    END AS Education_Label,

    -- Environment Satisfaction
    CASE 
        WHEN EnvironmentSatisfaction = 1 THEN 'Low'
        WHEN EnvironmentSatisfaction = 2 THEN 'Medium'
        WHEN EnvironmentSatisfaction = 3 THEN 'High'
        WHEN EnvironmentSatisfaction = 4 THEN 'Very High'
    END AS EnvironmentSatisfaction_Label,

    -- Job Involvement
    CASE 
        WHEN JobInvolvement = 1 THEN 'Low'
        WHEN JobInvolvement = 2 THEN 'Medium'
        WHEN JobInvolvement = 3 THEN 'High'
        WHEN JobInvolvement = 4 THEN 'Very High'
    END AS JobInvolvement_Label,

    -- Job Satisfaction
    CASE 
        WHEN JobSatisfaction = 1 THEN 'Low'
        WHEN JobSatisfaction = 2 THEN 'Medium'
        WHEN JobSatisfaction = 3 THEN 'High'
        WHEN JobSatisfaction = 4 THEN 'Very High'
    END AS JobSatisfaction_Label,

    -- Performance Rating
    CASE
        WHEN PerformanceRating = 1 THEN 'Low'
        WHEN PerformanceRating = 2 THEN 'Good'
        WHEN PerformanceRating = 3 THEN 'Excellent'
        WHEN PerformanceRating = 4 THEN 'Outstanding'
    END AS PerformanceRating_Label,

    -- Relationship Satisfaction
    CASE 
        WHEN RelationshipSatisfaction = 1 THEN 'Low'
        WHEN RelationshipSatisfaction = 2 THEN 'Medium'
        WHEN RelationshipSatisfaction = 3 THEN 'High'
        WHEN RelationshipSatisfaction = 4 THEN 'Very High'
    END AS RelationshipSatisfaction_Label,

    -- Work Life Balance
    CASE 
        WHEN WorkLifeBalance = 1 THEN 'Bad'
        WHEN WorkLifeBalance = 2 THEN 'Good'
        WHEN WorkLifeBalance = 3 THEN 'Better'
        WHEN WorkLifeBalance = 4 THEN 'Best'
    END AS WorkLifeBalance_Label,

-- Veri setinde belirtilmeyen ama label olarak eklenebilecek diğer kategorik sütunları da ekleyelim:
    -- Job Level
    CASE 
        WHEN JobLevel = 1 THEN 'Entry Level'
        WHEN JobLevel = 2 THEN 'Junior'
        WHEN JobLevel = 3 THEN 'Mid-Level'
        WHEN JobLevel = 4 THEN 'Senior'
        WHEN JobLevel = 5 THEN 'Executive'
    END AS JobLevel_Label,

    -- Stock Option
    CASE 
        WHEN StockOptionLevel = 0 THEN 'None'
        WHEN StockOptionLevel = 1 THEN 'Low'
        WHEN StockOptionLevel = 2 THEN 'Medium'
        WHEN StockOptionLevel = 3 THEN 'High'
    END AS StockOptionLevel_Label

FROM Employees;
GO
