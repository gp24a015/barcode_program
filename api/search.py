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


APPID = os.environ["APPID"]


# 学習した商品名加工モデルの読み込み
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "product_name_model.pkl"
)

model_data = joblib.load(MODEL_PATH)

vectorizer = model_data["vectorizer"]
X = model_data["X"]
after_names = model_data["after"]


def jancode_to_name(code):

    url = (
        "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"
        f"?appid={APPID}&jan_code={code}&results=1"
    )

    try:
        with urlopen(url) as resp:
            res = json.load(resp)

    except URLError as err:
        print(err, file=sys.stderr)
        return None

    if "hits" in res and res["hits"]:
        return res["hits"][0]["name"]

    return None


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
            options={"write_text": True}
        )

        image_base64 = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        return "data:image/png;base64," + image_base64

    except Exception as err:

        print(
            "バーコード生成エラー:",
            err,
            file=sys.stderr
        )

        return None


def predict_product_name(product_name):

    # Yahooから取得した商品名をベクトル化
    query_vector = vectorizer.transform(
        [product_name]
    )

    # 学習データとの類似度を計算
    similarities = cosine_similarity(
        query_vector,
        X
    )[0]

    # 最も類似しているデータの番号
    best_index = similarities.argmax()

    # 一番高い類似度
    best_score = similarities[best_index]

    print("元の商品名:", product_name)
    print(
        "予測商品名:",
        after_names[best_index]
    )
    print(
        "類似度:",
        best_score
    )

    # 類似度が低すぎる場合
    if best_score < 0.2:

        print("類似する商品が見つかりませんでした")

        return product_name

    return after_names[best_index]


class handler(BaseHTTPRequestHandler):

    def do_POST(self):

        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        body = self.rfile.read(content_length)

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


        barcode_code = data.get("barcode")

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


        # Yahoo Shopping APIから商品名を取得
        product_name = jancode_to_name(
            barcode_code
        )

        # バーコード画像を生成
        barcode_image = generate_barcode(
            barcode_code
        )


        if product_name is not None:

            # 機械学習で商品名を加工
            product_name = predict_product_name(
                product_name
            )


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


        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.end_headers()


        response = {

            "barcode": barcode_code,

            "product_name": product_name,

            "barcode_image": barcode_image

        }


        self.wfile.write(

            json.dumps(
                response,
                ensure_ascii=False
            ).encode("utf-8")

        )
