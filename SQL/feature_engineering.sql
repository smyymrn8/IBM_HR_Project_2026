USE IBM_HR_DB;
GO

-- Feature engineering için bir görünüm(view) oluşturma: vw_HR_Feature_Engineering
-- Bu view, Employees tablosundaki verilerden yeni özellikler (features) türetmek için çeşitli hesaplamalar ve kategorik dönüşümler içerir.
CREATE OR ALTER VIEW vw_HR_Feature_Engineering AS
SELECT
    *,
    
    -- Salary fairness: Gelir adaleti için, her iş seviyesindeki ortalama gelire göre bireysel geliri normalize ediyoruz.
    -- Bu özellik, çalışanın geliri ile iş seviyesindeki ortalama geliri karşılaştırarak, gelir adaletini ölçer. Yüksek bir değer, çalışanın iş seviyesindeki ortalamanın üzerinde bir gelire sahip olduğunu gösterebilir.
    MonthlyIncome * 1.0 / JobLevel AS income_per_level,

    -- Salary gap: Her iş seviyesindeki ortalama gelire göre bireysel gelirin ne kadar farklı olduğunu gösterir.
    -- Pozitif değerler, bireysel gelirin ortalamanın üzerinde olduğunu, negatif değerler ise altında olduğunu gösterir.
    MonthlyIncome - AVG(MonthlyIncome) OVER (PARTITION BY JobLevel) AS salary_gap,

    -- Career stability: Çalışanın şirketteki kalıcılığını ölçmek için, şirket deneyimi ile toplam çalışma yılı arasındaki oranı hesaplıyoruz.
    -- Bu oran, çalışanın şirketteki deneyimini genel kariyer deneyimine göre değerlendirir. Yüksek bir oran, çalışanın şirkette uzun süre kalma eğiliminde olduğunu gösterebilir.
    YearsAtCompany * 1.0 / NULLIF(TotalWorkingYears,0) AS tenure_ratio,

    -- Promotion stagnation: Son promosyon sonrası geçen süreyi, şirketteki toplam yıl ile karşılaştırarak ölçer.
    -- Bu özellik, çalışanın son promosyonundan bu yana ne kadar süre geçtiğini ve bu sürenin şirket deneyimine göre nasıl bir oran oluşturduğunu gösterir. Yüksek bir değer, çalışanın uzun süredir terfi alamadığını gösterebilir.
    YearsSinceLastPromotion * 1.0 / NULLIF(YearsAtCompany,0) AS promotion_delay,

    -- Satisfaction index: Çalışanın iş tatminini ölçmek için, çeşitli tatmin anketlerinden alınan puanların ortalamasını hesaplıyoruz.
    -- Bu özellik, çalışanın genel iş tatminini tek bir indeks olarak sunar. Yüksek bir değer, çalışanın işinden daha memnun olduğunu gösterebilir.
    (
        JobSatisfaction +
        EnvironmentSatisfaction +
        WorkLifeBalance +
        RelationshipSatisfaction
    ) / 4.0 AS satisfaction_index,

    -- Career fairness: Gelir ile toplam çalışma yılı arasındaki oranı hesaplayarak, deneyime göre gelirin ne kadar olduğunu ölçer.
    -- Bu özellik, çalışanın deneyimine göre ne kadar gelir elde ettiğini gösterir. Yüksek bir değer, çalışanın deneyimine göre iyi bir gelir elde ettiğini gösterebilir.
    MonthlyIncome * 1.0 / NULLIF(TotalWorkingYears,0) AS income_per_experience,

    -- Commute stress: Evden işe gidip gelme mesafesini, yaşa göre normalize ederek, işe gidip gelme stresini ölçer.
    -- Bu özellik, çalışanın yaşına göre evden işe gidip gelme mesafesini değerlendirir. Yüksek bir değer, çalışanın yaşına göre uzun bir mesafe kat ettiğini gösterebilir.
    DistanceFromHome * 1.0 / NULLIF(Age,0) AS commute_ratio,

    -- Age group: Yaş gruplarını kategorize ederek, çalışanları genç, orta yaş ve kıdemli olarak sınıflandırır.
    CASE
        WHEN Age < 30 THEN 'Young'
        WHEN Age BETWEEN 30 AND 40 THEN 'Mid Age'
        ELSE 'Senior'
    END AS age_group,

    -- Income levels: Gelir seviyelerini düşük, orta ve yüksek olarak kategorize eder.
    CASE
        WHEN MonthlyIncome < 3000 THEN 'Low Income'
        WHEN MonthlyIncome BETWEEN 3000 AND 7000 THEN 'Medium Income'
        ELSE 'High Income'
    END AS income_level,

    -- Tenure groups (Company Experience): Çalışanın şirketteki deneyimine göre yeni çalışan, junior, orta kıdemli ve uzun kıdemli olarak sınıflandırır.
    CASE
        WHEN YearsAtCompany < 2 THEN 'New Employee'
        WHEN YearsAtCompany BETWEEN 2 AND 5 THEN 'Junior'
        WHEN YearsAtCompany BETWEEN 6 AND 10 THEN 'Mid Tenure'
        ELSE 'Long Tenure'
    END AS tenure_group,

    -- Career stage: Yaş ve şirketteki deneyime göre kariyer aşamalarını erken kariyer, orta kariyer ve kıdemli kariyer olarak sınıflandırır.
    CASE
        WHEN Age < 30 AND YearsAtCompany < 3 THEN 'Early Career'
        WHEN Age BETWEEN 30 AND 40 THEN 'Mid Career'
        ELSE 'Senior Career'
    END AS career_stage,

    -- Training group: Çalışanın son yıl içinde aldığı eğitim sayısına göre düşük ve yüksek olarak kategorize eder. (Skill development için) 
    CASE
        WHEN TrainingTimesLastYear <= 2 THEN 'Low'
        ELSE 'High'
    END AS training_group,

    -- Company count group: Çalışanın daha önce kaç şirkette çalıştığını, az ve çok olarak kategorize eder. (Career stability için) 
    CASE
        WHEN NumCompaniesWorked <= 2 THEN 'Few'
        ELSE 'Many'
    END AS company_count_group,

    -- Distance group: Evden işe gidip gelme mesafesini, yakın, orta ve uzak olarak kategorize eder. (Commute stress için)
    CASE
        WHEN DistanceFromHome <= 5 THEN 'Near'
        WHEN DistanceFromHome <= 15 THEN 'Medium'
        ELSE 'Far'
    END AS distance_group

FROM Employees;
GO



-- Kontrol sorgusu
SELECT 
    Age_Group,
    COUNT(*) AS EmployeeCount
FROM vw_HR_Feature_Engineering
GROUP BY Age_Group

ORDER BY EmployeeCount DESC;
