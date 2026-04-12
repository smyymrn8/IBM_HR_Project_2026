import pandas as pd
from scipy.stats import shapiro

# ---------------------------------------------------
# 1) VERİ SETİNİ OKU
# ---------------------------------------------------
df = pd.read_csv(r"C:\Users\cakir\OneDrive\Desktop\ik_veriler.csv")

# ---------------------------------------------------
# 2) ATTRITION DEĞİŞKENİNİ SAYISALLAŞTIR
# Yes -> 1
# No  -> 0
# ---------------------------------------------------
df["Attrition"] = df["Attrition"].map({"Yes": 1, "No": 0})

# ---------------------------------------------------
# 3) TEST EDİLECEK SAYISAL DEĞİŞKENLERİ BELİRLE
# Şimdilik en anlamlı olanlarla başlıyoruz ve önceki haftada kullandığım sayısal değişkenleri kullanıyoruz.
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
# 4) HER DEĞİŞKEN İÇİN, ATTRITION=1 VE ATTRITION=0
# GRUPLARINDA AYRI AYRI SHAPIRO-WILK TESTİ YAP
# ---------------------------------------------------
for var in numeric_vars:

    # Sadece ilgili sütunları al, eksik verileri temizle
    temp_df = df[[var, "Attrition"]].dropna()

    # İki grubu ayır
    group_yes = temp_df[temp_df["Attrition"] == 1][var]
    group_no = temp_df[temp_df["Attrition"] == 0][var]

    # Shapiro-Wilk testi çok büyük örneklemlerde bazen problem çıkarabilir.
    # O yüzden güvenli olması için en fazla 5000 gözlemle test ediyoruz.
    # Bizim veri setimiz zaten 1470 civarında olduğu için genelde sorun olmaz,
    # ama yine de bu yapı daha güvenlidir.
    sample_yes = group_yes.sample(min(len(group_yes), 5000), random_state=42)
    sample_no = group_no.sample(min(len(group_no), 5000), random_state=42)

    # Eğer gruplardan biri çok küçükse test yapılamayabilir
    if len(sample_yes) < 3 or len(sample_no) < 3:
        print(f"{var} için yeterli veri yok, atlanıyor.")
        continue

    # Shapiro-Wilk testleri
    stat_yes, p_yes = shapiro(sample_yes)
    stat_no, p_no = shapiro(sample_no)

    # Sonuçları kaydet
    results.append({
        "Variable": var,
        "Group_Yes_Count": len(group_yes),
        "Group_No_Count": len(group_no),
        "Shapiro_Stat_Yes": stat_yes,
        "Shapiro_p_Yes": p_yes,
        "Shapiro_Stat_No": stat_no,
        "Shapiro_p_No": p_no
    })

# ---------------------------------------------------
# 5) SONUÇLARI DATAFRAME'E ÇEVİR
# ---------------------------------------------------
results_df = pd.DataFrame(results)

# p değerlerini daha okunur hale getirmek için bilimsel gösterim kullanalım
results_df["Shapiro_p_Yes"] = results_df["Shapiro_p_Yes"].apply(lambda x: f"{x:.3e}")
results_df["Shapiro_p_No"] = results_df["Shapiro_p_No"].apply(lambda x: f"{x:.3e}")

# İstatistik değerlerini yuvarlayalım
results_df["Shapiro_Stat_Yes"] = results_df["Shapiro_Stat_Yes"].round(4)
results_df["Shapiro_Stat_No"] = results_df["Shapiro_Stat_No"].round(4)

# ---------------------------------------------------
# 6) YORUM SÜTUNLARI EKLE
# p > 0.05 ise "yaklaşık normal"
# p <= 0.05 ise "normal değil"
# ---------------------------------------------------
def yorumla(p_text):
    p = float(p_text)
    if p > 0.05:
        return "Yaklaşık normal"
    else:
        return "Normal değil"

results_df["Yes_Group_Comment"] = results_df["Shapiro_p_Yes"].apply(yorumla)
results_df["No_Group_Comment"] = results_df["Shapiro_p_No"].apply(yorumla)

# ---------------------------------------------------
# 7) SONUÇLARI YAZDIR
# ---------------------------------------------------
print("\n--- SHAPIRO-WILK NORMALLİK TESTİ SONUÇLARI ---\n")
print(results_df)