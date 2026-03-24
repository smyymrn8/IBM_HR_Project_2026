
# bu dosyada tekli değişkenlerin uygun grafikler ile görselleştirilmesi ve korelayson matrixinin gösterimi için kodlar bulunmaktadır.


import numpy as np
import pandas as pd   # verileri çekmek için
import matplotlib.pyplot as plt  # görselleştirme için
import plotly.express as px # görselleştirme için

# ikili değişkenlerin görselleştirilmesi için
import plotly.graph_objects as go 

# matrix kısmında
import seaborn as sns
import matplotlib.pyplot as plt


# veri setimiz temiz olduğundan dolayı (kontroller yapıldı) csv dosyası üzerinden okuyarak görselleştirmeyi yaptık.
df = pd.read_csv(r"C:\Users\cakir\OneDrive\Desktop\Bitirme projesi ile ilgili\ik_veriler.csv")
print(df.head())  # veri setinin ilk 5 satırını kontorl etmek için


# kategorik, sayısal değişkenler için attrition oranlarını göstermek ve kod tekrarını azaltmak amacıyla fonksiyon tanımlanması
def plot_categorical_attrition(dataframe, column, title):
    """
    Kategorik değişkenler için:
    - Bar: toplam kişi sayısı
    - Line: attrition oranı
    """

    # Toplam kişi sayısı
    total = dataframe.groupby(column).size().reset_index(name="TotalCount")

    # Attrition sayısı
    attr = dataframe.groupby(column)["Attrition"] \
        .apply(lambda x: (x=="Yes").sum()) \
        .reset_index(name="AttritionCount")

    # Birleştirme
    df_plot = pd.merge(total, attr, on=column)

    # Oran hesaplama
    df_plot["AttritionRate"] = df_plot["AttritionCount"] / df_plot["TotalCount"]

    import plotly.graph_objects as go

    fig = go.Figure()

    # Bar → toplam kişi
    fig.add_trace(go.Bar(
        x=df_plot[column],
        y=df_plot["TotalCount"],
        name="Total Employees",
        opacity=0.6
    ))

    # Line → attrition oranı
    fig.add_trace(go.Scatter(
        x=df_plot[column],
        y=df_plot["AttritionRate"],
        mode="lines+markers",
        name="Attrition Rate",
        yaxis="y2"
    ))

    # İki eksenli yapı
    fig.update_layout(
        title=title,
        xaxis_title=column,
        yaxis=dict(title="Employee Count"),
        yaxis2=dict(
            title="Attrition Rate",
            overlaying="y",
            side="right"
        )
    )

    fig.show()

def plot_numeric_histogram_attrition(dataframe, column, title):
    """
    Sayısal değişkenler için:
    Attrition'a göre dağılımı histogram ile gösterir.
    """
    fig = px.histogram(
        dataframe,
        x=column,
        color="Attrition",
        barmode="group",
        color_discrete_map={"Yes": "red", "No": "blue"},
        title=title
    )

    fig.show()

# literatürde incelenen değişkenler 
# OverTime, JobSatisfaction, JobLevel, Department...



# ============================================================
# 1. KATEGORİK / ORDINAL DEĞİŞKENLER
# Bu değişkenlerde grouped bar chart daha uygundur.
# Çünkü bu veriler kategori veya seviye mantığında çalışır.
# ============================================================

categorical_columns = [
    ("Education", "Education vs Attrition"),
    ("RelationshipSatisfaction", "Relationship Satisfaction vs Attrition"),
    ("EnvironmentSatisfaction", "Environment Satisfaction vs Attrition"),
    ("JobInvolvement", "Job Involvement vs Attrition"),
    ("JobLevel", "Job Level vs Attrition"),
    ("JobSatisfaction", "Job Satisfaction vs Attrition"),
    ("StockOptionLevel", "Stock Option Level vs Attrition"),
    ("OverTime", "OverTime vs Attrition"),
    ("Department", "Department vs Attrition"),
    ("JobRole", "JobRole vs Attrition"),
    ("MaritalStatus", "Marital Status vs Attrition"), # evli/bekar farkı da etkili olabilir.
    ("Gender", "Gender vs Attrition"),
    ("BusinessTravel", "Business Travel vs Attrition"),
    ("EducationField", "Education Field vs Attrition")
]

for col, title in categorical_columns:
    plot_categorical_attrition(df, col, title)


# ============================================================
# 2. SAYISAL DEĞİŞKENLER - HISTOGRAM
# Sayısal değişkenlerin Attrition gruplarına göre dağılımı inceleniyor.
# ============================================================

numeric_hist_columns = [
    ("DistanceFromHome", "Distance From Home vs Attrition"),
    ("NumCompaniesWorked", "Num Companies Worked vs Attrition"),
    ("PercentSalaryHike", "Percent Salary Hike vs Attrition"),
    ("TrainingTimesLastYear", "Training Times Last Year vs Attrition"),
    ("MonthlyIncome", "Monthly Income vs Attrition"),
    ("YearsAtCompany", "Years At Company vs Attrition"),
    ("TotalWorkingYears", "Total Working Years vs Attrition"),
    ("YearsInCurrentRole", "Years In Current Role vs Attrition"),
    ("YearsSinceLastPromotion", "Years Since Last Promotion vs Attrition"),
    ("YearsWithCurrManager", "Years With Current Manager vs Attrition")

]

for col, title in numeric_hist_columns:
    plot_numeric_histogram_attrition(df, col, title)

# Yaş gruplama (çok önemli!)
df["AgeGroup"] = pd.cut(
    df["Age"],
    bins=[18, 25, 35, 45, 55, 65],
    labels=["18-25", "26-35", "36-45", "46-55", "56+"]
)

# Toplam kişi
total = df.groupby("AgeGroup").size().reset_index(name="TotalCount")

# Attrition sayısı
attr = df.groupby("AgeGroup")["Attrition"] \
    .apply(lambda x: (x == "Yes").sum()) \
    .reset_index(name="AttritionCount")

# Birleştir
age_data = pd.merge(total, attr, on="AgeGroup")

# Oran hesapla
age_data["AttritionRate"] = age_data["AttritionCount"] / age_data["TotalCount"]

# Grafik
fig = go.Figure()

# Bar → kişi sayısı
fig.add_trace(go.Bar(
    x=age_data["AgeGroup"],
    y=age_data["TotalCount"],
    name="Employee Count",
    opacity=0.5
))

# Line → attrition oranı
fig.add_trace(go.Scatter(
    x=age_data["AgeGroup"],
    y=age_data["AttritionRate"],
    mode="lines+markers",
    name="Attrition Rate",
    yaxis="y2"
))

# Çift eksen
fig.update_layout(
    title="Age Group vs Attrition Rate",
    xaxis_title="Age Group",
    yaxis=dict(title="Employee Count"),
    yaxis2=dict(
        title="Attrition Rate",
        overlaying="y",
        side="right"
    )
)

fig.show()

# buraya kadar tekli değişkenlerin attrition ile ilişkisini incelemiş olduk. 


# Her değişkenin yalnızca attrition ile ilişkisini görmek için korelasyon matrixini uyguluyoruz.
# korelasyonda sayısal veya binary değişkenler üzerinden gidilir. 
# kategorik değişken(yes/no) olduğu için korelasyon matrixinde göstermek adına burada sayısal değişkene çevirip kullanıyoruz.

df["AttritionBinary"] = df["Attrition"].map({"Yes":1, "No":0})

# OverTime'da binary olduğu için sayısala çeviriyoruz.
df["OverTime"] = df["OverTime"].map({"Yes":1, "No":0}) 

# Tüm sayısal değişkenler arasındaki ilişkileri görmek için korelasyon matrisi oluşturulmuştur.
corr_matrix = df.select_dtypes(include='number').corr()

# Mask oluştur (üst üçgeni göster)
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

plt.figure(figsize=(12,8))
sns.heatmap(
    corr_matrix,
    mask=mask,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    linewidths=0.5
)

plt.title("Correlation Matrix (Upper Triangle)")
plt.show()

# Korelasyon değerleri -1 ile +1 arasında değişir:
# +1 → güçlü pozitif ilişki
# -1 → güçlü negatif ilişki
# 0 → ilişki yok

# attrition için olan korelasyon (FEATURE SELECTION).
# sayısal kolonlar seçiliyor.
numeric_cols = df.select_dtypes(include='number').columns

# AttritionBinary hariç diğerlerini al.
numeric_cols = [col for col in numeric_cols if col != "AttritionBinary"]

# Her değişkenin Attrition ile ilişkisi hesaplanıyor
correlations = {}

for col in numeric_cols:
    corr = df[col].corr(df["AttritionBinary"])
    correlations[col] = corr
# Bu feature importance(özellik önemi) gibi davranır.

# DataFrame'e çevir
corr_df = pd.DataFrame.from_dict(correlations, orient='index', columns=['Correlation'])

# Büyükten küçüğe sırala
corr_df = corr_df.sort_values(by="Correlation", ascending=False)

print(corr_df)

# Bu analiz, feature selection (ön eleme) amacıyla kullanılır.
# ve bunun görselleştirilmesi.
import plotly.express as px

fig = px.bar(
    corr_df,
    x=corr_df.index,
    y="Correlation",
    title="Correlation with Attrition",
)

fig.show()
