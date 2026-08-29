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

APPID = os.environ["APPID"]


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
        ean = barcode.get("ean13", code[:12], writer = ImageWriter())
        buffer = BytesIO()
        ean.write(buffer, options={"write_text":True})

        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return "data:image/png;base64," + image_base64

    except Exception as err:
        print(err, file=sys.stderr)

        return None

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
                    {"error": "JSONの形式が正しくありません"},
                    ensure_ascii=False
                ).encode("utf-8")
            )

            return

        barcode = data.get("barcode")

        if not barcode:

            self.send_response(400)
            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )
            self.end_headers()

            self.wfile.write(
                json.dumps(
                    {"error": "JANコードがありません"},
                    ensure_ascii=False
                ).encode("utf-8")
            )

            return

        product_name = jancode_to_name(barcode)

        barcode_image = generate_barcode(barcode)

        if product_name is None:

            self.send_response(404)
            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )
            self.end_headers()

            self.wfile.write(
                json.dumps(
                    {"error": "商品が見つかりません"},
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
            "barcode": barcode,
            "product_name": product_name,
            "barcode_image": barcode_image
        }

        self.wfile.write(
            json.dumps(
                response,
                ensure_ascii=False
            ).encode("utf-8")
        )