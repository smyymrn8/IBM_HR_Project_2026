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

    df = pd.read_sql("SELECT * FROM vw_HR_Feature_Engineering", engine)

    # target encoding
    if df["Attrition"].dtype == object:
        df["Attrition"] = df["Attrition"].map({"Yes": 1, "No": 0})
    
    return df


# ============================================================
# HYPOTHESIS SEGMENTS (PYTHON ENGINEERING)
def create_segments(df):

    df["H1_Burnout"] = np.where(
        (df["OverTime"] == "Yes") & (df["JobSatisfaction"] <= 2),
        "Risk", "Other"
    )

    df["H2_WorkLife"] = np.where(
        (df["OverTime"] == "Yes") & (df["WorkLifeBalance"] <= 2),
        "Risk", "Other"
    )

    df["H3_Travel"] = np.where(
        (df["BusinessTravel"] == "Travel_Frequently") &
        (df["WorkLifeBalance"] <= 2),
        "Risk", "Other"
    )

    df["H4_Satisfaction"] = np.where(
        (df["JobSatisfaction"] <= 2) &
        (df["EnvironmentSatisfaction"] <= 2),
        "Risk", "Other"
    )

    # Satisfaction index: İş memnuniyeti, ortam memnuniyeti ve yaşam dengesi memnuniyetinin ortalaması. 2.5'in altı düşük memnuniyet olarak kabul edilir. 
    df["H5"] = np.where(
        df["satisfaction_index"] < 2.5, "Low", "High")

    df["H6_Income_Tenure"] = np.where(
        (df["income_level"] == "Low Income") &
        (df["tenure_group"] == "New Employee"),
        "Risk", "Other"
    )

    df["H7_Involvement"] = np.where(
        (df["JobInvolvement"] <= 2) &
        (df["JobSatisfaction"] <= 2),
        "Risk", "Other"
    )

    df["H8_Companies"] = np.where(
        (df["company_count_group"] == "Many") &
        (df["JobSatisfaction"] <= 2),
        "Risk", "Other"
    )

    df["H9"] = np.where(
        df["income_per_experience"] < df["income_per_experience"].median(),
        "Low", "High"
    )

    df["H10_Tenure"] = np.where(
        (df["tenure_ratio"] < 0.3) &
        (df["JobSatisfaction"] <= 2),
        "Risk", "Other"
    )

    df["H11_3var"] = np.where(
        (df["age_group"] == "Young") &
        (df["income_level"] == "Low Income") &
        (df["promotion_delay"] > 0.5),
        "Risk", "Other"
    )

    df["H12"] = np.where(
        df["tenure_ratio"] < 0.3, "Low", "High")

    df["H13_Performance"] = np.where(
        (df["PerformanceRating"] >= 3) &
        (df["JobSatisfaction"] <= 2),
        "Risk", "Other"
    )

    df["H14"] = np.where(
        (df["StockOptionLevel"] <= 1) &
        (df["JobLevel"] <= 2),
        "Risk", "Other"
    )

    df["H15"] = np.where(
        df["EducationField"] != df["JobRole"],
        "Mismatch", "Match"
    )

    df["H16_Training"] = np.where(
        (df["training_group"] == "Low") &
        (df["JobInvolvement"] <= 2),
        "Risk", "Other"
    )

    df["H17_Hopping"] = np.where(
        (df["company_count_group"] == "Many") &
        (df["tenure_group"] == "New Employee"),
        "Risk", "Other"
    )

    df["burnout_risk"] = np.where(
        (df["OverTime"] == "Yes") &
        (df["satisfaction_index"] < 2.5),
        "High", "Low"
    )

    df["salary_segment"] = np.where(
        df["salary_gap"] < 0,
        "Underpaid", "Fair"
    )

    df["early_career_risk"] = np.where(
        (df["age_group"] == "Young") &
        (df["tenure_group"] == "New Employee"),
        "High", "Low"
    )

    df["promotion_risk"] = np.where(
        (df["promotion_delay"] > 0.5) &
        (df["JobSatisfaction"] <= 2),
        "High", "Low"
    )

    df["commute_risk"] = np.where(
        (df["distance_group"] == "Far") &
        (df["OverTime"] == "Yes"),
        "High", "Low"
    )

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

    categorical = [
        "H1_Burnout","H2_WorkLife","H3_Travel","H4_Satisfaction",
        "H5","H6_Income_Tenure","H7_Involvement","H8_Companies",
        "H9","H10_Tenure","H11_3var","H12","H13_Performance",
        "H14","H15","H16_Training","H17_Hopping",
        "burnout_risk","salary_segment","early_career_risk",
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
def chi_square(df, col):

    temp = df[[col, "Attrition"]].dropna()
    table = pd.crosstab(temp[col], temp["Attrition"])

    if table.shape[0] < 2:
        return None

    chi2, p, _, expected = chi2_contingency(table)

    n = table.values.sum()
    r, c = table.shape

    cramer_v = np.sqrt(chi2 / (n * (min(r-1, c-1))))

    # ASSUMPTION CHECK
    min_exp = expected.min()
    low_exp_ratio = (expected < 5).sum() / expected.size

    if min_exp < 1:
        assumption = "Not valid"
    elif low_exp_ratio > 0.20:
        assumption = "Caution"
    else:
        assumption = "OK"

    return chi2, p, cramer_v, assumption


def mann_whitney(df, col):

    temp = df[[col, "Attrition"]].dropna()

    g1 = temp[temp["Attrition"] == 1][col]
    g0 = temp[temp["Attrition"] == 0][col]

    if len(g1) < 5 or len(g0) < 5:
        return None

    stat, p = mannwhitneyu(g1, g0)

    # EFFECT SIZE (r)
    n1 = len(g1)
    n2 = len(g0)

    r = 1 - (2 * stat) / (n1 * n2)

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

        if col not in df.columns:
            continue

        res = mann_whitney(df, col)
        if res is None:
            continue

        stat, p, effect, med1, med0 = res

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

    reject, p_adj, _, _ = multipletests(df["p_value"], method="fdr_bh")

    df["p_adj"] = p_adj
    df["significant"] = reject

    def calc(row):

        s = 0

        if row["p_adj"] < 0.05:
            s += 3

        if row["Test"] == "Chi-Square" and row["Effect"] > 0.2:
            s += 2

        if row["Test"] == "Mann-Whitney" and abs(row["Effect"]) > 0.3:
            s += 2

        if row.get("Assumption") == "OK":
            s += 1
        elif row.get("Assumption") == "Not valid":
            s -= 1

        return s

    df["Score"] = df.apply(calc, axis=1)

    return df


# ============================================================
# INTERPRETATION 
def add_interpretation(df):

    df = df.copy() 
    df = df.drop(columns=["Interpretation"], errors="ignore")

    def interpret(row):

        if row["p_adj"] >= 0.05:
            return "Not statistically significant → no strong evidence of relationship with Attrition."

        effect = row.get("Effect", 0)
        direction = row.get("Direction", "")

        # Chi-square yorum
        if row["Test"] == "Chi-Square":

            if effect > 0.3:
                strength = "strong"
            elif effect > 0.2:
                strength = "moderate"
            else:
                strength = "weak"

            return f"""
Significant relationship detected.
Effect size (Cramer's V): {effect:.3f} → {strength} association.
Risk pattern: category differences exist in Attrition distribution.
"""

        # Mann-Whitney yorum
        else:

            if abs(effect) > 0.3:
                strength = "strong"
            elif abs(effect) > 0.15:
                strength = "moderate"
            else:
                strength = "weak"

            return f"""
Significant difference detected.
Effect size (rank-biserial r): {effect:.3f} → {strength} effect.
Direction: {direction}.
Interpretation: numeric feature differs between Attrition groups.
"""

    df["Interpretation"] = df.apply(interpret, axis=1)

    return df


# ============================================================
# MAIN
if __name__ == "__main__":

    df = run()
    df = score(df)
    df = add_interpretation(df) 

    top10 = df.sort_values("Score", ascending=False).head(10)

    print("\n===== TOP 10 HYPOTHESES =====\n")
    print(top10[["Feature","Test","p_value","p_adj","Effect","Score"]])

    df.to_csv("hypothesis_results.csv", index=False)
    top10.to_csv("top10_hypothesis_results.csv", index=False)

