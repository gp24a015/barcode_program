import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# ==============================
# 学習データ読み込み
# ==============================

data = pd.read_csv("training_data.csv")

X = data["word"]
y = data["label"]


# ==============================
# 文字列を数値化
# ==============================

vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(1, 3)
)

X_vectorized = vectorizer.fit_transform(X)


# ==============================
# 機械学習
# ==============================

model = LogisticRegression(
    max_iter=1000
)

model.fit(X_vectorized, y)


# ==============================
# モデルとVectorizerを保存
# ==============================

model_data = {
    "vectorizer": vectorizer,
    "model": model
}

joblib.dump(
    model_data,
    "product_classifier.pkl"
)

print("学習完了")
print("保存先: product_classifier.pkl")