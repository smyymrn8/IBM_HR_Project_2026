import pandas as pd
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

# ---------------------------------------------------
# 1) VERİ SETİNİ OKU
# ---------------------------------------------------
# df = pd.read_csv(r"C:\Users\cakir\OneDrive\Desktop\ik_veriler.csv")
from pathlib import Path

# Proje yapısına uygun dinamik yol
current_dir = Path(__file__).resolve().parent
csv_path = current_dir.parent / "DATA" / "WA_Fn-UseC_-HR-Employee-Attrition.csv"

df = pd.read_csv(csv_path)
print(f"CSV başarıyla yüklendi: {csv_path}")
# ---------------------------------------------------
# 2) ATTRITION DEĞİŞKENİNİ SAYISALLAŞTIR
# Yes -> 1
# No  -> 0
# ---------------------------------------------------
# Attrition için güvenli dönüşüm
if df["Attrition"].dtype == 'object':
    df["Attrition"] = df["Attrition"].map({"Yes": 1, "No": 0})

# ---------------------------------------------------
# 3) ANALİZ EDİLECEK SAYISAL DEĞİŞKENLER
# ---------------------------------------------------
numeric_vars = [
    "Age",
    "DistanceFromHome",
    "MonthlyIncome",
    "NumCompaniesWorked",
    "PercentSalaryHike",
    "TotalWorkingYears",
    "TrainingTimesLastYear",
    "YearsAtCompany",
    "YearsInCurrentRole",
    "YearsSinceLastPromotion",
    "YearsWithCurrManager"
]

# Sonuçları burada tutacağız
results = []

# ---------------------------------------------------
# 4) HER SAYISAL DEĞİŞKEN İÇİN MANN-WHITNEY U TESTİ
# ---------------------------------------------------
for var in numeric_vars:

    # Eksik değerleri temizle
    temp_df = df[[var, "Attrition"]].dropna()

    # İki grubu ayır
    group_yes = temp_df[temp_df["Attrition"] == 1][var]
    group_no = temp_df[temp_df["Attrition"] == 0][var]

    # Eğer gruplardan biri boşsa testi yapamayız
    if len(group_yes) == 0 or len(group_no) == 0:
        print(f"{var} için yeterli veri yok, atlanıyor.")
        continue

    # Mann-Whitney U testi
    # alternative="two-sided" -> iki grup arasında fark var mı diye bakıyoruz
    u_stat, p_value = mannwhitneyu(group_yes, group_no, alternative="two-sided")

    # Tanımlayıcı istatistikler de ekleyelim ki yön yorumlayabilelim
    results.append({
        "Variable": var,
        "Yes_Count": len(group_yes),
        "No_Count": len(group_no),

        # Ortalama ve medyanları eklemek yorum için çok yararlı
        "Yes_Mean": group_yes.mean(),
        "No_Mean": group_no.mean(),
        "Yes_Median": group_yes.median(),
        "No_Median": group_no.median(),

        # Standart sapma ekleyelim
        "Yes_STD": group_yes.std(),
        "No_STD": group_no.std(),

        # Test sonucu
        "U_Statistic": u_stat,
        "p_value": p_value
    })

# ---------------------------------------------------
# 5) SONUÇLARI DATAFRAME'E ÇEVİR
# ---------------------------------------------------
results_df = pd.DataFrame(results)

# p değerine göre sırala
results_df = results_df.sort_values("p_value").reset_index(drop=True)

# ---------------------------------------------------
# 6) ÇOKLU TEST DÜZELTMESİ (FDR)
# Birden fazla değişken test ettiğimiz için ekliyoruz
# ---------------------------------------------------
reject, p_adj, _, _ = multipletests(results_df["p_value"], alpha=0.05, method="fdr_bh")
results_df["p_adj"] = p_adj
results_df["Significant_after_FDR"] = reject

# ---------------------------------------------------
# 7) YORUM SÜTUNU EKLE
# Medyanlara göre hangi grubun daha yüksek olduğunu belirtelim
# ---------------------------------------------------
def yorum_satiri(row):
    if row["Yes_Median"] > row["No_Median"]:
        return "Attrition=1 grubunda daha yüksek"
    elif row["Yes_Median"] < row["No_Median"]:
        return "Attrition=0 grubunda daha yüksek"
    else:
        return "Medyanlar eşit"

results_df["Median_Comparison"] = results_df.apply(yorum_satiri, axis=1)

# ---------------------------------------------------
# 8) GÖRÜNÜMÜ DAHA OKUNABİLİR HALE GETİR
# ---------------------------------------------------
for col in ["Yes_Mean", "No_Mean", "Yes_Median", "No_Median", "Yes_STD", "No_STD", "U_Statistic"]:
    results_df[col] = results_df[col].round(4)

# p-value ve p_adj'yi bilimsel gösterimle yaz
results_df["p_value"] = results_df["p_value"].apply(lambda x: f"{x:.3e}")
results_df["p_adj"] = results_df["p_adj"].apply(lambda x: f"{x:.3e}")

# ---------------------------------------------------
# 9) SADECE GEREKLİ SÜTUNLARI YAZDIR
# ---------------------------------------------------
print("\n--- MANN-WHITNEY U TESTİ SONUÇLARI ---\n")
print(
    results_df[
        [
            "Variable",
            "Yes_Median",
            "No_Median",
            "U_Statistic",
            "p_value",
            "p_adj",
            "Significant_after_FDR",
            "Median_Comparison"
        ]
    ]
)

# ---------------------------------------------------
# 10) CSV OLARAK KAYDET
# ---------------------------------------------------
# results_df.to_csv(
#     r"C:\Users\cakir\OneDrive\Desktop\mann_whitney_results.csv",
#     index=False,
#     encoding="utf-8-sig"
# )

# print("\nSonuçlar masaüstüne 'mann_whitney_results.csv' olarak kaydedildi.")

# ---------------------------------------------------
# 10) CSV OLARAK KAYDET (DİNAMİK YOL)
# ---------------------------------------------------
# Kayıt yapılacak klasörü, kodun bulunduğu yerin bir üst dizini (proje ana dizini) olarak belirliyoruz
output_path = current_dir.parent / "mann_whitney_results.csv"

# Veriyi kaydet
results_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"\nSonuçlar proje ana dizinine başarıyla kaydedildi: {output_path}")

