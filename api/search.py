import os
import json
from urllib.request import urlopen
from urllib.error import URLError

APPID = os.environ["APPID"]

def jancode_to_name(code):

    url = (
        "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"
        f"?appid={APPID}"
        f"&jan_code={code}"
        "&results=1"
    )

    try:
        with urlopen(url) as resp:
            res = json.load(resp)

    except URLError as err:
        print(err)
        return None

    if "hits" in res and res["hits"]:
        return res["hits"][0]["name"]

    return None

def handler(request):
    # POST以外を拒否
    if request.method != "POST":
        return {
            "error": "POST method is required"
        }, 405

    # JSONを取得
    try:
        data = request.get_json()

    except Exception:
        return {
            "error": "JSONの形式が正しくありません"
        }, 400

    # JANコードを取得
    barcode = data.get("barcode")

    if not barcode:
        return {
            "error": "JANコードがありません"
        }, 400

    # 商品名を取得
    product_name = jancode_to_name(barcode)

    # 商品が見つからない
    if product_name is None:
        return {
            "error": "商品が見つかりません"
        }, 404

    # 成功
    return {
        "barcode": barcode,
        "product_name": product_name
    }, 200