console.log("products.js!!");

$(document).ready(() => {

    console.log("商品一覧ページ");

    // localStorageから商品を取得
    let products = JSON.parse(
        localStorage.getItem("products") || "[]"
    );

    const productList = $("#product_list");


    // =========================
    // 商品がない場合
    // =========================
    if (products.length === 0) {

        productList.html(
            "<p>商品がありません</p>"
        );

        return;
    }


    // =========================
    // 商品一覧を表示
    // =========================
    products.forEach((product, index) => {

        const item = `
            <div class="product_item">

                <div>
                    ${index + 1}. ${product.name}
                </div>

                <div>
                    JAN：${product.barcode}
                </div>

                <div>
                    ${product.date}
                </div>

            </div>
        `;

        productList.append(item);
    });


    // =========================
    // 履歴削除
    // =========================
    $("#clear_products").click(() => {

        const result = confirm(
            "商品履歴をすべて削除しますか？"
        );

        if (!result) {
            return;
        }

        localStorage.removeItem("products");

        location.reload();
    });

});