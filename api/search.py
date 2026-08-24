import os
import sys
import json
from urllib.request import urlopen
from urllib.error import URLError
from http.server import BaseHTTPRequestHandler

APPID = os.environ["APPID"]


def jancode_to_name(code):
    product_name = None
    url = f"https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch?appid={APPID}&jan_code={code}&results=1"

    try:
        with urlopen(url) as resp:
            res = json.load(resp)

    except URLError as err:
        print(err.reason, file=sys.stderr)
        return None


    if "hits" in res and res['hits']:
        product_name = res["hits"][0]["name"]
    return product_name

class handler(BaseHTTPRequestHandler):

    def do_POST(self):

        # JavaScriptから送られてきたデータのサイズ
        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        # データを受け取る
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

            response = {
                "error": "JSONの形式が正しくありません"
            }

            self.wfile.write(
                json.dumps(
                    response,
                    ensure_ascii=False
                ).encode("utf-8")
            )

            return

        # JANコードを取得
        barcode = data.get("barcode")

        if not barcode:

            self.send_response(400)
            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )
            self.end_headers()

            response = {
                "error": "JANコードがありません"
            }

            self.wfile.write(
                json.dumps(
                    response,
                    ensure_ascii=False
                ).encode("utf-8")
            )

            return

        # 商品名を取得
        product_name = jancode_to_name(barcode)

        # 商品が見つからなかった場合
        if product_name is None:

            self.send_response(404)
            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )
            self.end_headers()

            response = {
                "error": "商品が見つかりません"
            }

            self.wfile.write(
                json.dumps(
                    response,
                    ensure_ascii=False
                ).encode("utf-8")
            )

            return

        # 成功
        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.end_headers()

        response = {
            "barcode": barcode,
            "product_name": product_name
        }

        self.wfile.write(
            json.dumps(
                response,
                ensure_ascii=False
            ).encode("utf-8")
        )