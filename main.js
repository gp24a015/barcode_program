console.log("main.js!!");

$(document).ready(() => {
    console.log("Ready!!");
});

let detected = false;


// ==============================
// 商品検索
// ==============================
function searchProduct(barcode) {

    console.log("商品検索:", barcode);

    // JANコードを表示
    $("#my_result").text(barcode);

    // Python APIへJANコードを送信
    fetch("/api/search", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            barcode: barcode
        })

    })

    .then(response => {
        return response.json();
    })

    .then(data => {

        console.log("APIからの返答:", data);

        // 商品名
        if (data.product_name) {

            $("#product_name").text(
                data.product_name
            );

        } else {

            $("#product_name").text(
                "商品が見つかりません"
            );
        }

        // バーコード画像
        if (data.barcode_image) {

            $("#my_barcode").html(
                `<img src="${data.barcode_image}" alt="バーコード画像">`
            );

        } else {

            $("#my_barcode").html(
                "<div>バーコード画像を生成できませんでした</div>"
            );
        }

    })

    .catch(error => {

        console.error("APIエラー:", error);

        $("#product_name").text(
            "商品検索でエラーが発生しました"
        );

    });
}


// ==============================
// Start
// ==============================
$("#my_start").click(() => {

    console.log("Start!!");

    // カメラ画面を再表示
    $("#my_quagga").css("display", "block");

    // 新しく読み取りを開始
    detected = false;

    Quagga.init({

        inputStream: {
            name: "Live",
            type: "LiveStream",
            target: document.getElementById("my_quagga")
        },

        decoder: {
            readers: ["ean_reader"]
        }

    }, err => {

        if (err) {
            console.log(err);
            return;
        }

        console.log("Initialization finished!!");

        Quagga.start();

    });
});


// ==============================
// バーコード検出処理
// ==============================
Quagga.onDetected(result => {

    // すでに読み取っていたら無視
    if (detected) return;

    detected = true;

    const barcode = result.codeResult.code;

    console.log("バーコード:", barcode);

    // カメラを停止
    Quagga.stop();

    // 商品検索
    searchProduct(barcode);

});


// ==============================
// Quaggaの処理状況
// ==============================
Quagga.onProcessed(result => {

    if (result == null) return;

    if (typeof(result) != "object") return;

    if (result.boxes == undefined) return;

    const ctx = Quagga.canvas.ctx.overlay;

    const canvas = Quagga.canvas.dom.overlay;

    ctx.clearRect(
        0,
        0,
        parseInt(canvas.width),
        parseInt(canvas.height)
    );

    Quagga.ImageDebug.drawPath(
        result.box,

        {
            x: 0,
            y: 1
        },

        ctx,

        {
            color: "blue",
            lineWidth: 5
        }
    );

});


// ==============================
// Stop
// ==============================
$("#my_stop").click(() => {

    console.log("Stop!!");

    Quagga.stop();

    detected = false;

});


// ==============================
// テキスト入力による商品検索
// ==============================
$("#barcode_search").click(() => {

    const barcode = $("#barcode_input").val().trim();

    console.log("入力されたバーコード:", barcode);

    // JANコード13桁チェック
    if (!/^\d{13}$/.test(barcode)) {

        alert("13桁のJANコードを入力してください");

        return;
    }

    // カメラを停止
    Quagga.stop();

    // 商品検索
    searchProduct(barcode);

});