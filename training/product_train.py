import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# ==============================
# 学習データを読み込む
# ==============================

data = pd.read_csv("training_data.csv")

X = data["word"]
y = data["label"]

# ==============================
# 機械学習モデル
# ==============================

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            analyzer="char",
            ngram_range=(1, 3)
        )
    ),
    (
        "classifier",
        LogisticRegression()
    )
])

# ==============================
# 学習
# ==============================
model.fit(X, y)
print("学習完了")


# ==============================
# 学習結果を保存
# ==============================

joblib.dump(
    model,
    "../api/product_classifier.pkl"
)

print("モデルを保存しました")