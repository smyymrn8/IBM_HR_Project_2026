import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
from statsmodels.stats.multitest import multipletests
import platform
from sqlalchemy import create_engine

# 1. İşletim sistemine göre bağlantı ayarlarını seç
system_platform = platform.system()

try:
    if system_platform == "Darwin":  # MAC 
        engine = create_engine("mssql+pymssql://sa:StrongPass123!@localhost:1433/IBM_HR_DB")
        conn = engine.connect()
        print("Mac/Docker üzerinden SQLAlchemy (pymssql) ile bağlanıldı.")
        
    else:  # WINDOWS
        # pyodbc ve Trusted Connection kullanır
        import pyodbc   # oluşturduğumuz 3 kategorik değişken csv dosyasında değildi, tekrar oluşturmamak için sql ortamından çekmeye karar verdik. 
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=IBM_HR_DB;"
            "Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_str)
        print("Windows üzerinden pyodbc (Trusted Connection) ile bağlanıldı.")

    # 2. Veriyi çekme
    query = """
    SELECT 
        EmployeeNumber, 
        age_group, 
        income_level, 
        tenure_group 
    FROM vw_HR_Feature_Engineering
    """
    
    # pandas hem pyodbc objesini hem de sqlalchemy engine objesini destekler
    sql_df = pd.read_sql(query, conn)
    print("SQL verisi başarıyla çekildi.")

    # kontrol amaçlı yazdırıyoruz
    print(sql_df.head())
    print(sql_df.columns)
    print(sql_df.shape)

finally:
    # işimiz bittiğinde bağlantıyı güvenli bir şekilde kapatıyoruz
    conn.close()


# Burada ana veriyi csv üzerinden çekiyoruz, çünkü chi-square testini uygularken hem sql'den çektiğimiz 3 kategorik değişkeni hem de csv'deki diğer kategorik değişkenleri kullanacağız.

# Proje yapısına uygun dinamik yol 
from pathlib import Path
current_dir = Path(__file__).resolve().parent
csv_path = current_dir.parent / "DATA" / "WA_Fn-UseC_-HR-Employee-Attrition.csv"
df = pd.read_csv(csv_path)
print(f"CSV başarıyla yüklendi: {csv_path}")


# Attrition için güvenli dönüşüm
if df["Attrition"].dtype == 'object':
    df["Attrition"] = df["Attrition"].map({"Yes": 1, "No": 0})


# SQL'den çektiğimiz yeni kategorik değişkenleri ana veri setine birleştiriyoruz.
# EmployeeNumber ortak anahtar olarak kullanılıyor
df = pd.merge(df, sql_df, on="EmployeeNumber", how="left")

# Kontrol: yeni sütunlar geldi mi? diye kontorl ediyoruz.
print("\nBirleştirilmiş veri:")
print(df.head())
print(df.columns)

# Eksik geldi mi diye hızlı kontrol
print("\nSQL'den gelen yeni sütunlardaki boş değer sayıları:")
print(df[["age_group", "income_level", "tenure_group"]].isnull().sum())


# 11 adet kategorik veri bulunuyor, bunları chi-square testine tabii tutacağız.
categorical_vars = [
    "OverTime",
    "JobSatisfaction",
    "EnvironmentSatisfaction",
    "JobInvolvement",
    "RelationshipSatisfaction",
    "Department",
    "JobRole",
    "MaritalStatus",
    "BusinessTravel",
    "JobLevel",
    "StockOptionLevel",
    "age_group",
    "income_level",
    "tenure_group"
]

results = []

for var in categorical_vars:
    table = pd.crosstab(df[var], df["Attrition"])

    # Geçersiz tablo varsa atla(uygun tablo oluşmadıysa)
    if table.shape[0] < 2 or table.shape[1] < 2:
        continue

    # Chi-square testi uygulama aşaması
    chi2, p, dof, expected = chi2_contingency(table)

    # Toplam gözlem sayısı
    n = table.values.sum()
    # Satır ve sütun sayısı
    r, c = table.shape

    # Cramer's V
    cramer_v = np.sqrt(chi2 / (n * min(r - 1, c - 1)))

    # Varsayım kontrolleri
    min_expected = expected.min()
    low_expected_count = (expected < 5).sum()
    low_expected_ratio = (expected < 5).sum() / expected.size

    results.append({
        "Variable": var,
        "Chi2": chi2,
        "p_value": p,
        "dof": dof,
        "Cramers_V": cramer_v,
        "Min_Expected": min_expected,
        "Low_Expected_Cell_Count": low_expected_count,
        "Low_Expected_Cell_Ratio": low_expected_ratio
    })

results_df = pd.DataFrame(results).sort_values("p_value").reset_index(drop=True)

# Çoklu test düzeltmesi (Benjamini-Hochberg) -> tercih etme sebebimiz test sayısının fazla olması ve bu yüzden yanlış pozitif sonuçların artma ihtimalinin yüksek olması.
# burada birden fazla sayısal test yaptığımızdan dolayı hatanın büyümesi bekleniyor bundan dolayı da çoklu test düzeltmesi yaparak sonuçları daha güvenilir hale getireceğiz.
# multipletests fonksiyonu bize düzeltilmiş p değerlerini ve hangi sonuçların anlamlı olduğunu verecek.

reject, p_adj, _, _ = multipletests(results_df["p_value"], alpha=0.05, method="fdr_bh")
results_df["p_adj"] = p_adj
results_df["Significant_after_FDR"] = reject
results_df["Significant_0_05"] = results_df["p_value"] < 0.05


# varsayımların belli düzeyde yorumlanması
def check_assumption(row):
    if row["Min_Expected"] < 1:
        return "Uygun değil"
    elif row["Low_Expected_Cell_Ratio"] > 0.20:
        return "Dikkatli yorumlanmalı"
    else:
        return "Uygun"

results_df["Assumption_Status"] = results_df.apply(check_assumption, axis=1)


# Sayıların düzenlenmesi
results_df["Chi2"] = results_df["Chi2"].round(4)
results_df["p_value"] = results_df["p_value"].apply(lambda x: f"{x:.2e}")
results_df["Cramers_V"] = results_df["Cramers_V"].round(4)
results_df["p_adj"] = results_df["p_adj"].apply(lambda x: f"{x:.2e}")


#sonuçların yazdırılması
print("\n--- Kİ-KARE SONUÇLARI ---\n")
print(
    results_df[
        ["Variable", "Chi2", "p_value", "p_adj", "Cramers_V", "Significant_after_FDR"]
    ]
)
