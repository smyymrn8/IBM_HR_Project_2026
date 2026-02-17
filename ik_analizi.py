import pandas as pd  # veri temizleme ve analiz için pandas kütüphanesi
import sqlite3 #akademik olarak sqlite öneriliyor.

dosya_yolu = "C:/Users/cakir/OneDrive/Desktop/Bitirme ile ilgili/ik_veriler.csv"

try:
    df = pd.read_csv(dosya_yolu)
    print(df.head())

except FileNotFoundError:
    print(f"Hata: '{dosya_yolu}' dosyası bulunamadı.")


df.shape # satır sayisi kontrol edilecek
df.columns #sütun isimleri kontrol edilecek
df.info() # veri tipleri ve eksik değerler kontrol edilecek

#kategorik verilerin sayısal verilere dönüştürülmesi ile SQL'de daha temiz sorgular yazılabilecek.

df["Attrition"] = df["Attrition"].map({
    "Yes": 1,
    "No": 0
})

df["OverTime"] = df["OverTime"].map({
    "Yes": 1,
    "No": 0
})

df = df[df["TotalWorkingYears"] <= df["Age"]]
df = df[df["YearsAtCompany"] <= df["TotalWorkingYears"]]


db_yolu = "C:/Users/cakir/OneDrive/Desktop/Bitirme ile ilgili/ik_veritabani.db"

conn = sqlite3.connect(db_yolu)

df.to_sql(
    name ="tbl_ik_verileri",
    con = conn,
    if_exists="replace",
    index=False
)

kontrol_sorgusu = """
SELECT COUNT(*) AS toplam_kayit
FROM tbl_ik_verileri;
"""

pd.read_sql(kontrol_sorgusu, conn)

conn.close()
