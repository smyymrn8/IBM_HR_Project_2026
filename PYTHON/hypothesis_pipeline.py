import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from scipy.stats import chi2_contingency, mannwhitneyu
from statsmodels.stats.multitest import multipletests


# ============================================================
# LOAD DATA FROM SQL SERVER DATABASE (ASSUMING PRE-ENGINEERED VIEW) 
def load_data():

    engine = create_engine(
        "mssql+pymssql://sa:StrongPass123!@localhost:1433/IBM_HR_DB"
    )

    df = pd.read_sql("SELECT * FROM dbo.vw_HR_Feature_Engineering", engine)

    # target encoding
    if df["Attrition"].dtype == object:
        df["Attrition"] = df["Attrition"].map({"Yes": 1, "No": 0})
    
    return df


# ============================================================
# HYPOTHESIS SEGMENTS (PYTHON ENGINEERING)
def create_segments(df):

    # H1: Overtime yapan ve düşük iş memnuniyeti olan çalışanlar daha yüksek tükenmişlik(burnout) riski taşır. 
    df["H1_Burnout"] = np.where(
        (df["OverTime"] == "Yes") & (df["JobSatisfaction"] <= 2),
        "Risk", "Other"
    )

    # H2: Overtime yapan ve düşük yaşam dengesi memnuniyeti olan çalışanlar daha yüksek iş-yaşam dengesi riski taşır.
    df["H2_OverTime_WorkLife"] = np.where(
        (df["OverTime"] == "Yes") & (df["WorkLifeBalance"] <= 2),
        "Risk", "Other"
    )

    # H3: Sık seyahat eden ve düşük iş-yaşam dengesi memnuniyeti olan çalışanlar daha yüksek seyahat stresi riski taşır. 
    df["H3_Travel_WorkLife"] = np.where(
        (df["BusinessTravel"] == "Travel_Frequently") &
        (df["WorkLifeBalance"] <= 2),
        "Risk", "Other"
    )

    # H4: Düşük iş memnuniyeti ve düşük ortam memnuniyeti olan çalışanlar daha yüksek tatminsizlik riski taşır.
    df["H4_Satisfaction"] = np.where(
        (df["JobSatisfaction"] <= 2) &
        (df["EnvironmentSatisfaction"] <= 2),
        "Risk", "Other"
    )

    # H5(satisfaction index): İş memnuniyeti, ortam memnuniyeti ve yaşam dengesi memnuniyetinin ortalaması. 2.5'in altı düşük memnuniyet olarak kabul edildi. 
    df["H5_satisfaction_index"] = np.where(
        df["satisfaction_index"] < 2.5, "Low", "High")

    # H6: Düşük gelir seviyesine sahip ve yeni çalışan olan bireyler daha yüksek finansal stres riski taşır. 
    df["H6_Income_Tenure"] = np.where(
        (df["income_level"] == "Low Income") &
        (df["tenure_group"] == "New Employee"),
        "Risk", "Other"
    )

    # H7: Düşük iş katılımı ve düşük iş memnuniyeti olan çalışanlar daha yüksek disengagement riski taşır. 
    df["H7_Involvement"] = np.where(
        (df["JobInvolvement"] <= 2) &
        (df["JobSatisfaction"] <= 2),
        "Risk", "Other"
    )

    # H8: Çok sayıda şirkette çalışmış ve düşük iş memnuniyeti olan çalışanlar daha yüksek iş değiştirme riski taşır. 
    df["H8_Companies_JobSatisfaction"] = np.where(
        (df["company_count_group"] == "Many") &
        (df["JobSatisfaction"] <= 2),
        "Risk", "Other"
    )

    # H9: Geliri tecrübesine oranla düşük olan çalışanlar daha yüksek finansal stres riski taşır. 
    df["H9_Income_Experience"] = np.where(
        df["income_per_experience"] < df["income_per_experience"].median(),
        "Low", "High"
    )

    # H10: Şirkette kısa süredir çalışan ve düşük iş memnuniyeti olan bireyler daha yüksek risk taşır. 
    df["H10_Tenure_JobSatisfaction"] = np.where(
        (df["tenure_ratio"] < 0.3) &
        (df["JobSatisfaction"] <= 2),
        "Risk", "Other"
    )

    # H11: Genç yaş grubunda, düşük gelir seviyesine sahip ve uzun süre terfi almamış çalışanlar daha yüksek risk taşır. 
    df["H11_3var"] = np.where(
        (df["age_group"] == "Young") &
        (df["income_level"] == "Low Income") &
        (df["promotion_delay"] > 0.5),
        "Risk", "Other"
    )

    # H12: Şirketteki toplam tecrübesine göre kısa süredir çalışan bireyler daha yüksek risk taşır. 
    df["H12_Tenure_Companies"] = np.where(
        df["tenure_ratio"] < 0.3, "Low", "High")

    # H13: Düşük performans değerlendirmesi alan ve düşük iş memnuniyeti olan çalışanlar daha yüksek risk taşır. 
    df["H13_Performance"] = np.where(
        (df["PerformanceRating"] >= 3) &
        (df["JobSatisfaction"] <= 2),
        "Risk", "Other"
    )

    # H14: Düşük seviyede hisse senedi opsiyonuna sahip ve düşük iş seviyesinde çalışanlar daha yüksek risk taşır. 
    df["H14_StockOption_JobLevel"] = np.where(
        (df["StockOptionLevel"] <= 1) &
        (df["JobLevel"] <= 2),
        "Risk", "Other"
    )

    # H15: Eğitim alanı ile iş rolü arasında uyumsuzluk olan çalışanlar daha yüksek risk taşır. 
    df["H15_Education_JobRole"] = np.where(
        df["EducationField"] != df["JobRole"],
        "Mismatch", "Match"
    )

    # H16: Kısa eğitim süresi ve düşük iş katılımı olan çalışanlar daha yüksek risk taşır. 
    df["H16_Training_JobInvolvement"] = np.where(
        (df["training_group"] == "Low") &
        (df["JobInvolvement"] <= 2),
        "Risk", "Other"
    )

    # H17: Çok sayıda şirkette çalışmış ve yeni çalışan olan bireyler daha yüksek iş değiştirme riski taşır. 
    df["H17_JobHopping"] = np.where(
        (df["company_count_group"] == "Many") &
        (df["tenure_group"] == "New Employee"),
        "Risk", "Other"
    )

    # Ek segmentler: Bu segmentler, birden fazla risk faktörünü birleştirerek daha güçlü risk göstergeleri oluşturmayı amaçlar. 
    # Overtime yapan ve düşük memnuniyetli çalışanlar yüksek tükenmişlik riski taşır. 
    df["burnout_risk"] = np.where(
        (df["OverTime"] == "Yes") &
        (df["satisfaction_index"] < 2.5),
        "High", "Low"
    )

    # Geliri tecrübesine oranla düşük olan çalışanlar daha yüksek finansal stres riski taşır. 
    df["salary_segment_risk"] = np.where(
        df["salary_gap"] < 0,
        "Underpaid", "Fair"
    )

    # Genç yaş grubunda, düşük gelir seviyesine sahip ve uzun süre terfi almamış çalışanlar daha yüksek risk taşır. 
    df["early_career_risk"] = np.where(
        (df["age_group"] == "Young") &
        (df["tenure_group"] == "New Employee"),
        "High", "Low"
    )

    # Promosyon gecikmesi uzun ve düşük iş memnuniyeti olan çalışanlar daha yüksek risk taşır. 
    df["promotion_risk"] = np.where(
        (df["promotion_delay"] > 0.5) &
        (df["JobSatisfaction"] <= 2),
        "High", "Low"
    )

    # Evden işe gidip gelme mesafesi uzak ve overtime yapan çalışanlar daha yüksek risk taşır. 
    df["commute_risk"] = np.where(
        (df["distance_group"] == "Far") &
        (df["OverTime"] == "Yes"),
        "High", "Low"
    )

    # Overtime yapan, düşük memnuniyetli ve düşük gelir seviyesine sahip çalışanlar daha yüksek composite risk taşır. 
    df["composite_risk"] = np.where(
        (df["OverTime"] == "Yes") &
        (df["satisfaction_index"] < 2.5) &
        (df["income_level"] == "Low Income"),
        "High", "Low"
    )

    return df


# ============================================================
# HYPOTHESIS LIST (23 TOTAL)
def get_features():
    # Bu listeler, oluşturulan segmentler ve diğer önemli özellikler dahil olmak üzere, hipotez testlerinde kullanılacak kategorik ve sayısal özellikleri tanımlar. 

    categorical = [
        "H1_Burnout","H2_OverTime_WorkLife","H3_Travel_WorkLife","H4_Satisfaction",
        "H5_satisfaction_index","H6_Income_Tenure","H7_Involvement","H8_Companies_JobSatisfaction",
        "H9_Income_Experience","H10_Tenure_JobSatisfaction","H11_3var","H12_Tenure_Companies","H13_Performance",
        "H14_StockOption_JobLevel","H15_Education_JobRole","H16_Training_JobInvolvement","H17_JobHopping",
        "burnout_risk","salary_segment_risk","early_career_risk",
        "promotion_risk","commute_risk","composite_risk"
    ]

    numeric = [
        "Age","DistanceFromHome","MonthlyIncome","NumCompaniesWorked",
        "PercentSalaryHike","TotalWorkingYears","TrainingTimesLastYear",
        "YearsAtCompany","YearsInCurrentRole",
        "YearsSinceLastPromotion","YearsWithCurrManager"
    ]

    return categorical, numeric


# ============================================================
# TEST FUNCTIONS (Chi-Square for categorical, Mann-Whitney for numeric) 
def chi_square(df, col):    # Tests whether there is a significant association between the categorical feature and Attrition. Calculates chi-square statistic, p-value, Cramer's V effect size, and checks assumptions of the test. 

    temp = df[[col, "Attrition"]].dropna()
    table = pd.crosstab(temp[col], temp["Attrition"])
    # SAFETY CHECK: chi-square test requires at least 2 rows and 2 columns in the contingency table 
    if table.shape[0] < 2:
        return None
    
    chi2, p, _, expected = chi2_contingency(table)      # chi-square test statistic, p-value, degrees of freedom, expected frequencies 

    n = table.values.sum()  # total sample size
    r, c = table.shape      # number of rows and columns in the contingency table

    cramer_v = np.sqrt(chi2 / (n * (min(r-1, c-1))))   

    # ASSUMPTION CHECK : chi-square test assumes that expected frequencies should be >= 5 for at least 80% of the cells, and no cell should have expected frequency < 1 
    min_exp = expected.min()
    low_exp_ratio = (expected < 5).sum() / expected.size

    if min_exp < 1:
        assumption = "Not valid"
    elif low_exp_ratio > 0.20:
        assumption = "Caution"
    else:
        assumption = "OK"

    return chi2, p, cramer_v, assumption


def mann_whitney(df, col):      # Does not assume normal distribution. Tests whether the distribution of the numeric feature differs between the two groups defined by Attrition. 

    temp = df[[col, "Attrition"]].dropna()

    g1 = temp[temp["Attrition"] == 1][col]  # group with Attrition=1 
    g0 = temp[temp["Attrition"] == 0][col]  # group with Attrition=0    

    # SAFETY CHECK: Mann-Whitney test is not reliable with very small sample sizes in either group - at least 5 observations per group is a common rule of thumb 
    if len(g1) < 5 or len(g0) < 5:      
        return None

    stat, p = mannwhitneyu(g1, g0)      # Mann-Whitney U test statistic and p-value

    # EFFECT SIZE (r)
    r = 1 - (2*stat)/(len(g1)*len(g0))  # rank-biserial correlation as effect size for Mann-Whitney test

    return stat, p, r, g1.median(), g0.median()


# ============================================================
# PIPELINE EXECUTION
def run():

    df = load_data()
    df = create_segments(df)

    categorical, numeric = get_features()

    results = []

    # CHI-SQUARE TESTS FOR CATEGORICAL FEATURES 
    for col in categorical:

        if col not in df.columns:
            continue

        res = chi_square(df, col)
        if res is None:
            continue

        chi2, p, effect, assumption = res

        results.append({        
            "Feature": col,
            "Test": "Chi-Square",
            "Stat": chi2,
            "p_value": p,
            "Effect": effect,
            "Assumption": assumption
        })

    # MANN-WHITNEY TESTS FOR NUMERIC FEATURES 
    for col in numeric:

        # SAFETY CHECK: eğer veri setinde beklenen özelliklerden biri eksikse, test fonksiyonları hata verebilir. Bu kontrol, eksik özellikler durumunda o testi atlamamızı sağlar.
        if col not in df.columns:       
            continue

        res = mann_whitney(df, col)     # Mann-Whitney test is not performed if either group has less than 5 observations, so we check for None result to skip those cases. 
        if res is None:
            continue

        stat, p, effect, med1, med0 = res

        # med1 = Attrition=1 grubunun medyanı, med0 = Attrition=0 grubunun medyanı. Hangisi daha yüksekse o grupta o özellik daha belirgin olabilir. Bu, sonuçların yorumlanmasına yardımcı olabilir. 
        if med1 > med0:     
            direction = "Attrition=1 higher"
        elif med1 < med0:
            direction = "Attrition=0 higher"
        else:
            direction = "Equal"

        results.append({
            "Feature": col,
            "Test": "Mann-Whitney",
            "Stat": stat,
            "p_value": p,
            "Effect": effect,
            "Median_1": med1,
            "Median_0": med0,
            "Direction": direction
        })

    return pd.DataFrame(results)


# ============================================================
# SCORING + TOP 10 EXTRACTION 
def score(df):

    reject, p_adj, _, _ = multipletests(df["p_value"], method="fdr_bh")     # Benjamini-Hochberg yöntemi ile çoklu test düzeltmesi yaparak, p-değerlerini ayarlıyoruz ve hangi hipotezlerin reddedildiğini belirliyoruz. 

    df["p_adj"] = p_adj         # Ayarlanmış p-değerlerini sonuç DataFrame'ine ekliyoruz. Bu, hangi testlerin hala istatistiksel olarak anlamlı olduğunu görmemize yardımcı olur. 
    df["significant"] = reject  # Hangi testlerin istatistiksel olarak anlamlı olduğunu belirten bir sütun ekliyoruz. Bu, sonuçların yorumlanmasını kolaylaştırır. 

    def calc(row):

        s = 0

        if row["p_adj"] < 0.05:     # İstatistiksel olarak anlamlı bulunan hipotezlere puan veriyoruz. Bu, sonuçların önemini vurgulamak için kullanılır. 
            s += 3

        if row["Test"] == "Chi-Square" and row["Effect"] > 0.2:     # Cramer's V etkisi 0.2'den büyük olan kategorik özelliklere ekstra puan veriyoruz. Bu, sadece istatistiksel olarak anlamlı değil, aynı zamanda pratik olarak da önemli olan sonuçları öne çıkarmak içindir. 
            s += 2

        if row["Test"] == "Mann-Whitney" and abs(row["Effect"]) > 0.3:  # Rank-biserial r etkisi 0.3'ten büyük olan sayısal özelliklere ekstra puan veriyoruz. Bu, sadece istatistiksel olarak anlamlı değil, aynı zamanda pratik olarak da önemli olan sonuçları öne çıkarmak içindir.
            s += 2

        if row.get("Assumption") == "OK":   # Chi-Square testinin varsayımlarını karşılayan sonuçlara ekstra puan veriyoruz. Bu, testin sonuçlarının güvenilirliğini artırır.
            s += 1
        elif row.get("Assumption") == "Not valid":  # Chi-Square testinin varsayımlarını karşılamayan sonuçlara puan kırıyoruz. Bu, testin sonuçlarının güvenilirliğini azaltır.
            s -= 1

        return s

    df["Score"] = df.apply(calc, axis=1)    # Her bir hipotez için toplam puanı hesaplıyoruz. Bu, sonuçların önem sırasına göre sıralanmasını sağlar ve hangi hipotezlerin daha fazla dikkat gerektirdiğini gösterir. 

    return df


# ============================================================
# INTERPRETATION 
def add_interpretation(df): 
# Her bir hipotez testinin sonuçlarına göre yorumlar ekleyen bir fonksiyon. Bu, sonuçların daha anlaşılır ve eyleme dönüştürülebilir hale gelmesini sağlar. 

    df = df.copy()

    def interpret(row):

        if row["p_adj"] >= 0.05:    # İstatistiksel olarak anlamlı olmayan sonuçlar için yorum, bu özellik ile Attrition arasında güçlü bir ilişki olduğuna dair kanıt olmadığını belirtir. Bu, bu özelliklerin Attrition ile ilişkili olmadığını veya etkisinin çok küçük olduğunu gösterebilir. 
            return f"""
                Not statistically significant → no strong evidence of relationship with Attrition.
                Interpretation: no clear association detected.
                """

        effect = row.get("Effect", 0)           # Etkisi belirtilmemişse varsayılan olarak 0 alırız, bu da etkisiz bir ilişki olduğunu varsayar. Bu, yorumun devamında etkisinin gücünü değerlendirmemize yardımcı olur. 
        direction = row.get("Direction", "")    # Etki yönü belirtilmemişse boş string alırız, bu da etkisinin hangi yönde olduğunu belirtmez. Bu, yorumun devamında etkisinin yönünü değerlendirmemize yardımcı olur. 

        if row["Test"] == "Chi-Square":

            if effect > 0.3:            # Cramer's V etkisi 0.3'ten büyükse güçlü bir ilişki olduğunu belirtir. Bu, bu kategorik özelliğin Attrition ile güçlü bir şekilde ilişkili olduğunu gösterebilir. 
                strength = "strong"
            elif effect > 0.2:          
                strength = "moderate"
            else:
                strength = "weak"

            text = f"""
                Significant relationship detected.
                Effect size (Cramer's V): {effect:.3f} → {strength} association.
                Risk pattern: category differences exist in Attrition distribution.
                """

        else:

            if abs(effect) > 0.3:       # Rank-biserial r etkisi 0.3'ten büyükse güçlü bir ilişki olduğunu belirtir. Bu, bu sayısal özelliğin Attrition ile güçlü bir şekilde ilişkili olduğunu gösterebilir. 
                strength = "strong"
            elif abs(effect) > 0.15:
                strength = "moderate"
            else:
                strength = "weak"

            text = f"""
                Significant difference detected.
                Effect size (rank-biserial r): {effect:.3f} → {strength} effect.
                Direction: {direction}.
                Interpretation: numeric feature differs between Attrition groups.
                """
        return text

    df["Interpretation"] = df.apply(interpret, axis=1)     

    return df


# ============================================================
# MAIN
if __name__ == "__main__":

    df = run()
    df = score(df)

    # SAFETY: ensure no old column leakage
    df = df.drop(columns=["Interpretation"], errors="ignore")

    df = add_interpretation(df) 

    top10 = df.sort_values("Score", ascending=False).head(10)

    print("\n===== TOP 10 HYPOTHESES =====\n")
    print(top10[["Feature","Test","p_value","p_adj","Effect","Score","Interpretation"]])

    # Save results to CSV for further analysis or reporting. This allows us to keep a record of the hypothesis testing results and easily share them with stakeholders or use them in reports. 
    df.to_csv("hypothesis_results.csv", index=False)
    top10.to_csv("top10_hypothesis_results.csv", index=False)

    # DEBUG BLOCK : Bu blok, oluşturulan segmentlerin ve diğer özelliklerin gerçekten veri setinde yer alıp almadığını kontrol etmek için eklenmiştir. Eğer beklenen özellikler eksikse, bu durum test sonuçlarını etkileyebilir ve bu nedenle eksik özelliklerin hangileri olduğunu görmek önemlidir.
    # Debug kısmı, testlerin bittiğini ve hangi değişkenlerin sonuç tablosuna (muhtemelen düşük anlamlılık veya filtreleme nedeniyle) yansımadığını bize raporlamak için çalışır. Bu, hangi hipotezlerin test edildiğini ve hangi hipotezlerin eksik olduğunu görmemize yardımcı olur. 
    # Eksik hipotezler, test sonuçlarında yer almayan özellikler olabilir ve bu durum, testlerin kapsamını ve sonuçların yorumlanmasını etkileyebilir. Bu nedenle, bu debug bloğu, test sürecinin doğruluğunu ve kapsamını kontrol etmek için önemlidir.
    print("\n=== HYPOTHESIS COVERAGE DEBUG ===")

    categorical, numeric = get_features()   # get_features() fonksiyonunda tanımlanan kategorik ve sayısal özellikleri ayrı ayrı alırız. Bu, hangi özelliklerin test edildiğini ve hangi özelliklerin eksik olduğunu görmemize yardımcı olur. 
    all_features = categorical + numeric    # get_features() fonksiyonunda tanımlanan tüm özellikleri birleştirerek, testlerde kullanılması gereken tüm özelliklerin tam bir listesini oluştururuz. Bu, hangi özelliklerin test edildiğini ve hangi özelliklerin eksik olduğunu görmemize yardımcı olur.

    existing = df["Feature"].unique()   # run() tekrar çağırma -> zaten df var

    missing = set(all_features) - set(existing)     # get_features() fonksiyonunda tanımlanan özelliklerden hangilerinin test sonuçlarında yer almadığını belirler. Bu, eksik özelliklerin hangi hipotezlerde olduğunu görmemize yardımcı olur. 

    print("Missing due to filtering:")
    print(missing)

