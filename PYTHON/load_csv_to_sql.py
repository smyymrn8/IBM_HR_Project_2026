import pandas as pd
from sqlalchemy import create_engine

# CSV dosyanın yolu (proje klasöründe "data" klasörü varsa oraya koy)
csv_path = "/Users/smyymrn/Downloads/WA_Fn-UseC_-HR-Employee-Attrition.csv"

# CSV oku
df = pd.read_csv(csv_path)

# Kategorik verileri sayısal yap
df["Attrition"] = df["Attrition"].map({"Yes": 1, "No": 0})
df["OverTime"] = df["OverTime"].map({"Yes": 1, "No": 0})

# pymssql ile Docker MSSQL bağlantısı
engine = create_engine(
    "mssql+pymssql://sa:StrongPass123!@localhost:1433/IBM_HR_DB"
)

# Tabloya yaz (varsa sil, yenisi yazılır)
df.to_sql("Employees", con=engine, if_exists="replace", index=False)

# Kontrol
print("CSV başarıyla yüklendi.")
print(pd.read_sql("SELECT COUNT(*) AS toplam_kayit FROM Employees", engine))
