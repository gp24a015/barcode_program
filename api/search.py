import os
import json
from urllib.request import urlopen
from urllib.error import URLError

APPID = os.environ["APPID"]


def jancode_to_name(code):
    url = (
        "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"
        f"?appid={APPID}&jan_code={code}&results=1"
    )

    try:
        with urlopen(url) as resp:
            res = json.load(resp)
    except URLError:
        return None

    if "hits" in res and res["hits"]:
        return res["hits"][0]["name"]

    return None


def handler(request):
    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {
                "Content-Type": "application/json; charset=utf-8"
            },
            "body": json.dumps(
                {"error": "POST only"},
                ensure_ascii=False
            )
        }

    try:
        data = request.body
        if isinstance(data, bytes):
            data = json.loads(data)
        elif isinstance(data, str):
            data = json.loads(data)

    except Exception:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json; charset=utf-8"
            },
            "body": json.dumps(
                {"error": "JSONの形式が正しくありません"},
                ensure_ascii=False
            )
        }

    barcode = data.get("barcode")

    if not barcode:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json; charset=utf-8"
            },
            "body": json.dumps(
                {"error": "JANコードがありません"},
                ensure_ascii=False
            )
        }

    product_name = jancode_to_name(barcode)

    if product_name is None:
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json; charset=utf-8"
            },
            "body": json.dumps(
                {"error": "商品が見つかりません"},
                ensure_ascii=False
            )
        }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json; charset=utf-8"
        },
        "body": json.dumps(
            {
                "barcode": barcode,
                "product_name": product_name
            },
            ensure_ascii=False
        )
    }