import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================
# 学習データ読み込み
# =========================

data = pd.read_csv("training_data.csv")

before = data["before"].astype(str)
after = data["after"].astype(str)


# =========================
# 商品名をベクトル化
# =========================

vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(1, 3)
)

X = vectorizer.fit_transform(before)


# =========================
# モデル保存
# =========================

model_data = {
    "vectorizer": vectorizer,
    "X": X,
    "after": after.tolist()
}

joblib.dump(
    model_data,
    "../api/product_name_model.pkl"
)


print("学習完了")
print("モデルを保存しました")
print("../api/product_name_model.pkl")