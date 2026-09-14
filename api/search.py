import os
import json
import sys

from urllib.request import urlopen
from urllib.error import URLError
from http.server import BaseHTTPRequestHandler

import base64
from io import BytesIO

import barcode
from barcode.writer import ImageWriter

import joblib
from sklearn.metrics.pairwise import cosine_similarity


# Yahoo Shopping API
APPID = os.environ["APPID"]


# ========================================
# 商品名加工モデルの読み込み
# ========================================

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "product_name_model.pkl"
)

model_data = joblib.load(MODEL_PATH)

vectorizer = model_data["vectorizer"]
X = model_data["X"]
after_names = model_data["after"]


# ========================================
# Yahoo Shopping APIから商品名を取得
# ========================================

def jancode_to_name(code):

    url = (
        "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"
        f"?appid={APPID}&jan_code={code}&results=1"
    )

    try:

        with urlopen(url) as resp:
            res = json.load(resp)

    except URLError as err:

        print(
            "Yahoo APIエラー:",
            err,
            file=sys.stderr
        )

        return None


    if "hits" in res and res["hits"]:

        return res["hits"][0]["name"]


    return None


# ========================================
# バーコード画像を生成
# ========================================

def generate_barcode(code):

    try:

        ean = barcode.get(
            "ean13",
            code[:12],
            writer=ImageWriter()
        )

        buffer = BytesIO()

        ean.write(
            buffer,
            options={
                "write_text": True
            }
        )

        image_base64 = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        return (
            "data:image/png;base64,"
            + image_base64
        )

    except Exception as err:

        print(
            "バーコード生成エラー:",
            err,
            file=sys.stderr
        )

        return None


# ========================================
# 商品名を機械学習で加工
# ========================================

def predict_product_name(product_name):

    print()
    print("========== 商品名加工 ==========")
    print("元の商品名:", product_name)


    # Yahooの商品名をベクトル化
    query_vector = vectorizer.transform(
        [product_name]
    )


    # 学習データとの類似度を計算
    similarities = cosine_similarity(
        query_vector,
        X
    )[0]


    # 最も似ているデータを取得
    best_index = similarities.argmax()

    best_score = similarities[best_index]


    print(
        "最も似ている学習データ:",
        after_names[best_index]
    )

    print(
        "類似度:",
        best_score
    )


    # ====================================
    # 類似度が十分高い場合
    # ====================================

    if best_score >= 0.5:

        print("→ 類似度が高いため学習結果を採用")

        result = after_names[best_index]

    else:

        # =================================
        # 類似度が低い場合
        # =================================

        print(
            "→ 類似度が低いため元の商品名を使用"
        )

        result = product_name


    print("最終的な商品名:", result)
    print("================================")
    print()


    return result


# ========================================
# HTTPリクエスト
# ========================================

class handler(BaseHTTPRequestHandler):

    def do_POST(self):

        # --------------------------------
        # リクエストを読み込む
        # --------------------------------

        content_length = int(
            self.headers.get(
                "Content-Length",
                0
            )
        )

        body = self.rfile.read(
            content_length
        )


        # --------------------------------
        # JSONを解析
        # --------------------------------

        try:

            data = json.loads(body)

        except json.JSONDecodeError:

            self.send_response(400)

            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps(
                    {
                        "error":
                        "JSONの形式が正しくありません"
                    },
                    ensure_ascii=False
                ).encode("utf-8")
            )

            return


        # --------------------------------
        # JANコード取得
        # --------------------------------

        barcode_code = data.get(
            "barcode"
        )


        if not barcode_code:

            self.send_response(400)

            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps(
                    {
                        "error":
                        "JANコードがありません"
                    },
                    ensure_ascii=False
                ).encode("utf-8")
            )

            return


        # --------------------------------
        # Yahoo API
        # --------------------------------

        product_name = jancode_to_name(
            barcode_code
        )


        # --------------------------------
        # バーコード画像
        # --------------------------------

        barcode_image = generate_barcode(
            barcode_code
        )


        # --------------------------------
        # 商品名加工
        # --------------------------------

        if product_name is not None:

            product_name = predict_product_name(
                product_name
            )


        # --------------------------------
        # 商品が見つからない
        # --------------------------------

        if product_name is None:

            self.send_response(404)

            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps(
                    {
                        "error":
                        "商品が見つかりません"
                    },
                    ensure_ascii=False
                ).encode("utf-8")
            )

            return


        # --------------------------------
        # レスポンス
        # --------------------------------

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.end_headers()


        response = {

            "barcode":
                barcode_code,

            "product_name":
                product_name,

            "barcode_image":
                barcode_image
        }


        self.wfile.write(

            json.dumps(
                response,
                ensure_ascii=False
            ).encode("utf-8")

        )
