import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer


# 学習データ読み込み
data = pd.read_csv("training_data.csv")


# 文字列として扱う
before = data["before"].astype(str)
after = data["after"].astype(str)


# 商品名を文字単位で数値化
vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(1, 3)
)


# 加工前の商品名を学習
X = vectorizer.fit_transform(before)


# モデルとして保存するデータ
model_data = {
    "vectorizer": vectorizer,
    "X": X,
    "after": after.tolist()
}


# apiフォルダに保存
joblib.dump(
    model_data,
    "../api/product_name_model.pkl"
)


print("学習完了")
print("学習件数:", len(before))
print("モデルを保存しました")
print("../api/product_name_model.pkl")