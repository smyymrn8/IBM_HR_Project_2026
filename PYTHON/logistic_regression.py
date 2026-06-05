import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from pathlib import Path
from imblearn.over_sampling import SMOTE
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import seaborn as sns
import matplotlib.pyplot as plt
from hypothesis_pipeline import create_segments
from sklearn.model_selection import GridSearchCV

# Uyarıları bastırmak için 
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', category=FutureWarning)



# ========== VERİ YÜKLEME (SQL + Feature Engineering View)
def load_and_prepare_data():
    # SQL bağlantısı (Mac/Windows uyumlu)
    engine = create_engine("mssql+pymssql://sa:StrongPass123!@localhost:1433/IBM_HR_DB")
    
    # view'ı çekiyoruz
    query = "SELECT * FROM dbo.vw_HR_Feature_Engineering"
    df = pd.read_sql(query, engine)

    # Veriyi incelediğimizde, bazı kolonlarda NaN ve inf değerler olduğunu gördük. Bu değerler modelin performansını olumsuz etkileyebilir. 
    # Özellikle "promotion_delay", "tenure_ratio" ve "income_per_experience" kolonlarında NaN'lar var. Bu kolonlar, çalışanların terfi gecikmesi, kıdem oranı ve gelir/deneyim oranı gibi önemli bilgileri içeriyor olabilir. 
    # Bu nedenle, bu kolonlardaki NaN'ları 0 ile doldurmayı tercih ediyoruz. 0 değeri, bu özelliklerin etkisiz olduğunu varsayar, bu da modelin öğrenme sürecine zarar vermeden eksik verileri yönetmemize yardımcı olabilir. 
    # Sonsuz değerleri (inf) temizle
    df = df.replace([np.inf, -np.inf], np.nan)

    # Tespit ettiğimiz 3 kritik kolondaki NaN'ları 0 ile doldur
    fill_cols = ["promotion_delay", "tenure_ratio", "income_per_experience"]
    df[fill_cols] = df[fill_cols].fillna(0)

    """    
    # ========== Diğer kolonlarda NaN'lar var mı, varsa hangi kolonlarda ve kaç tane var? ========== 
    
    # En az bir tane NaN içeren tüm satırları getir
    df_nan_rows = df[df.isnull().any(axis=1)]

    print(f"Toplam boşluk içeren satır sayısı: {len(df_nan_rows)}")
    # Boşluk olan sütunları ve kaçar tane olduğunu listeler
    nan_columns = df.isnull().sum()
    print("--- Boş Değer İçeren Sütunlar ---")
    print(nan_columns[nan_columns > 0])

    # Boşluk olan satırları, nedenini anlayabileceğimiz kolonlarla birlikte görelim
    nan_rows = df[df.isnull().any(axis=1)]

    # İncelemek istediğimiz kritik kolonlar: 
    cols_to_check = ["YearsAtCompany", "TotalWorkingYears", "promotion_delay", "tenure_ratio", "income_per_experience"]

    print("--- Boşluk İçeren İlk 10 Satırın Analizi ---")
    print(nan_rows[cols_to_check].head(10))
    """

    # Analize katkısı olmayan veya ID niteliğindeki kolonları drop yapalım
    cols_to_drop = ["EmployeeCount", "StandardHours", "EmployeeNumber", "Over18"]
    df = df.drop(columns=cols_to_drop, errors="ignore")
    
    # Hedef değişkeni sayısallaştırma
    if df["Attrition"].dtype == object:
        df["Attrition"] = df["Attrition"].map({"Yes": 1, "No": 0})
    
    return df

df = load_and_prepare_data()

# ========== KATEGORİK DEĞİŞKENLERİ DÖNÜŞTÜRME (Encoding)
# SQL'den gelen tenure_group, career_stage gibi yeni kolonlar da dahil olmak üzere tüm metin tabanlı kolonları 0-1 formatına (Dummies) çeviriyoruz.
# Kategorik kolonları otomatik tespit et 
cat_cols = [col for col in df.drop('Attrition', axis=1).columns if df[col].dtype == 'object' or df[col].nunique() < 20]
df_final = pd.get_dummies(df, columns=cat_cols, drop_first=True)

# ========== VERİ SETİNİ AYIRMA (Train-Test Split)
# SMOTE uygulamadan önce ayırmalıyız. Çünkü SMOTE sadece eğitim setine uygulanmalı, test seti gerçek dünya dağılımını yansıtmalı. 
X = df_final.drop("Attrition", axis=1)
y = df_final["Attrition"]

# Stratify parametresi, eğitim ve test setlerinde hedef değişkenin (Attrition) dağılımının korunmasını sağlar. Bu, her iki setin de benzer oranlarda pozitif (1) ve negatif (0) örnekler içermesini garanti eder, bu da modelin performansını daha gerçekçi bir şekilde değerlendirmemize yardımcı olur.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# ========== ÖLÇEKLENDİRME (Scaling)
# Logistic Regression için ölçeklendirme önemlidir, özellikle sayısal değişkenler arasında büyük farklar varsa. 
# StandardScaler kullanarak tüm sayısal özellikleri ortalaması 0 ve standart sapması 1 olacak şekilde ölçeklendiriyoruz. Bu, modelin daha hızlı ve daha iyi öğrenmesine yardımcı olabilir.
scaler = StandardScaler()
# fit_transform ile önce eğitim setine göre scaler'ı öğreniyoruz (fit) ve ardından aynı scaler'ı kullanarak eğitim setini dönüştürüyoruz (transform). Bu, test setinin de aynı ölçeklendirme parametreleriyle dönüştürülmesini sağlar, böylece modelin gerçek dünya verisiyle tutarlı bir şekilde çalışmasını garanti eder.
X_train_scaled = scaler.fit_transform(X_train)      
print(np.isnan(X_train_scaled).any())   # True çıkarsa scaling sırasında bir hata oluşmuştur. np.isnan().any() sonucunun False çıkması, verilerinde fiziksel olarak boşluk kalmadığını ve fillna(0) işleminin başarılı olduğunu kanıtlıyor.
X_test_scaled = scaler.transform(X_test)

print(f"Hazırlık tamamlandı. Veri seti başarıyla yüklendi, kategorik değişkenler dönüştürüldü, eğitim ve test setlerine ayrıldı ve ölçeklendirildi.")
print(f"Eğitim seti boyutu: {X_train_scaled.shape}")
print(f"Test seti boyutu: {X_test_scaled.shape}")

# ========== SMOTE UYGULAMA (sadece eğitim setine)
# random_state=42 sayesinde sonuçlar her seferinde aynı çıkar. SMOTE, eğitim setindeki azınlık sınıfını çoğaltarak dengelemeye çalışır. 
smote = SMOTE(random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train)      
# SMOTE uygulandıktan sonra eğitim setindeki sınıf dağılımını kontrol ediyoruz. Bu, SMOTE'un azınlık sınıfını başarılı bir şekilde çoğaltıp çoğaltmadığını görmemize yardımcı olur. Eğer sınıflar dengelenmişse, her iki sınıfın da yaklaşık olarak aynı sayıda örneğe sahip olduğunu görmeliyiz.
print(f"\nSMOTE sonrası eğitim seti sınıf dağılımı: \n{pd.Series(y_train_res).value_counts()}")



# ========== MODEL 1: Genişletilmiş Değişkenli Model ========== 
# Tüm kolonların (SQL + CSV) dahil olduğu model

# max_iter=2000, solver='liblinear', C=0.1 parametreleri, modelin daha iyi öğrenmesini sağlamak için ayarlanmıştır. 
# max_iter=2000, modelin maksimum iterasyon sayısını artırarak daha karmaşık ilişkileri öğrenmesine olanak tanır. 
# solver='liblinear', küçük veri setleri ve L1 regularizasyonu için uygun bir algoritmadır. 
# C=0.1, regularizasyon gücünü artırarak modelin aşırı öğrenmesini (overfitting) önlemeye yardımcı olur.
# GridSearchCV kullanılmayacaksa alttaki iki satır kodu kullan: 
# log_model_1 = LogisticRegression(max_iter=2000, solver='liblinear', C=0.1, random_state=42)  
# log_model_1.fit(X_train_res, y_train_res)


# ===========================================================================================================
# 1. Denenecek parametreleri (grids) tanımlıyoruz
param_grid = {
    'C': [0.5, 0.8, 1, 1.2, 1.5, 2], # Regülarizasyon gücü
    'penalty': ['l1', 'l2'],        # Hata payı tipi (L1 bazı gereksiz kolonları sıfırlar)
    'solver': ['liblinear']         # L1 ve L2'yi destekleyen stabil çözücü
}

print("\n--- MODEL 1: GridSearchCV Optimizasyonu Başlatılıyor... ---")

# 2. GridSearchCV nesnesini oluşturuyoruz
# cv=5: Veriyi 5 farklı şekilde bölüp dene
# scoring='roc_auc': En iyi modeli ROC-AUC skoruna göre seç
grid_search = GridSearchCV(
    LogisticRegression(max_iter=2000, random_state=42), 
    param_grid, 
    cv=5, 
    scoring='roc_auc',
    verbose=1 # İşlemi takip edebilmek için
)

# 3. En iyi parametreleri bulmak için eğitimi başlatıyoruz
grid_search.fit(X_train_res, y_train_res)

# 4. En iyi sonuçları ve parametreleri raporluyoruz
print(f"En İyi Parametreler: {grid_search.best_params_}")
print(f"En İyi CV ROC-AUC Skoru: {grid_search.best_score_:.4f}")

# 5. Artık 'log_model_1' yerine en iyi modeli (best_estimator_) kullanabiliriz
log_model_1 = grid_search.best_estimator_
# ===========================================================================================================


# Model tahminleri (test seti üzerinde)
y_pred_1 = log_model_1.predict(X_test_scaled)
y_prob_1 = log_model_1.predict_proba(X_test_scaled)[:, 1]   # Olasılık değerleri (ROC-AUC için)

# Performans raporu
print("\n--- MODEL 1 GENİŞLETİLMİŞ DEĞİŞKENLİ MODEL SONUÇLARI ---")
print(classification_report(y_test, y_pred_1))  
# classification_report, modelin doğruluk, precision, recall ve F1-score gibi temel performans metriklerini detaylı bir şekilde sunar. 
# Bu metrikler, modelin pozitif sınıfı (1 - işten ayrılma) ne kadar iyi tahmin ettiğini gösterir. 
# Precision, modelin pozitif tahminlerinin ne kadarının doğru olduğunu gösterirken, recall, gerçek pozitiflerin ne kadarının doğru tahmin edildiğini gösterir. 
# F1-score ise precision ve recall'un harmonik ortalamasıdır ve dengesiz veri setlerinde daha anlamlı bir performans ölçütü sağlar.
# Support, her sınıf için gerçek örnek sayısını gösterir, bu da modelin hangi sınıflarda daha fazla veya daha az örneğe sahip olduğunu görmemize yardımcı olur.

# ROC-AUC Skoru : ROC-AUC, modelin pozitif sınıfı (1 - işten ayrılma) ne kadar iyi ayırabildiğini gösteren bir metriktir. 0.5 değeri, modelin rastgele tahmin ettiğini gösterirken, 1.0 değeri mükemmel bir ayrım gücüne sahip olduğunu gösterir.
auc_1 = roc_auc_score(y_test, y_prob_1)
print(f"ROC-AUC Skoru: {auc_1:.4f}\n\n")



# ========== MODEL 2: Top10 Hipotez Değişkenlenleri Odaklı Model ========== 
# Top 10 listesindeki değişkenleri encoded tablodan filtreliyoruz
top_10_base = ["Age", "tenure_group", "income_level", "TotalWorkingYears", 
               "MonthlyIncome", "PerformanceRating", "JobSatisfaction", "salary_gap", 
               "EnvironmentSatisfaction", "training_group", "JobInvolvement", 
               "StockOptionLevel", "JobLevel", "BusinessTravel", "WorkLifeBalance"]

# One-hot encoding sonrası isimler değiştiği için içerenleri seçiyoruz
# selected_cols, top_10_base listesinde yer alan temel değişken adlarını içeren encoded kolonları bulmak için bir liste oluşturuyoruz. Bu, encoded kolon adlarının top_10_base listesinde belirtilen temel değişken adlarını içermesi durumunda bu kolonları seçmemize olanak tanır. Bu şekilde, model 2'de sadece top 10 hipotez değişkenlerine odaklanarak daha spesifik bir model oluşturabiliriz.
selected_cols = [col for col in X_train.columns if any(h in col for h in top_10_base)]
print(selected_cols)        # kontrol edelim 

X_train_top10 = X_train[selected_cols]
X_test_top10 = X_test[selected_cols]

print(f"\nX_train_top10 sütun sayısı: {X_train_top10.shape[1]}")
print(f"y_train sütun sayısı: {len(y_train)}")

# Ölçeklendirme ve SMOTE (model 2 için) 
scaler_2 = StandardScaler()
X_train_top10_scaled = scaler_2.fit_transform(X_train_top10)
X_test_top10_scaled = scaler_2.transform(X_test_top10)

X_train_res_2, y_train_res_2 = smote.fit_resample(X_train_top10_scaled, y_train)

# Model 2 eğitimi 
# GridSearchCV kullanılmayacaksa alttaki iki satır kodu kullan: 
# log_model_2 = LogisticRegression(max_iter=2000, solver='liblinear', C=0.1, random_state=42)
# log_model_2.fit(X_train_res_2, y_train_res_2)


# ===========================================================================================================
print("\n--- MODEL 2: GridSearchCV Optimizasyonu Başlatılıyor... ---")

grid_search_2 = GridSearchCV(
    LogisticRegression(max_iter=2000, random_state=42), 
    param_grid, # Model 1'de kullandığımız hassaslaştırılmış grid
    cv=5, 
    scoring='roc_auc'
)

grid_search_2.fit(X_train_res_2, y_train_res_2)

print(f"Model 2 En İyi Parametreler: {grid_search_2.best_params_}")
print(f"En İyi CV ROC-AUC Skoru: {grid_search_2.best_score_:.4f}")
log_model_2 = grid_search_2.best_estimator_
# ===========================================================================================================


# Tahminler
y_pred_2 = log_model_2.predict(X_test_top10_scaled)
y_prob_2 = log_model_2.predict_proba(X_test_top10_scaled)[:, 1]

print("\n--- MODEL 2: TOP 10 HİPOTEZ DEĞİŞKENLERİ ODAKLI MODEL SONUÇLARI ---")
print(classification_report(y_test, y_pred_2))
print(f"ROC-AUC Skoru: {roc_auc_score(y_test, y_prob_2):.4f}\n")


