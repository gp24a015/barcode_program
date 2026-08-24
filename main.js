console.log("main.js!!");

$(document).ready(() => {
    console.log("Ready!!");
});

let detected = false;


// ==============================
// Start
// ==============================
$("#my_start").click(() => {

    console.log("Start!!");

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

    // JANコードを表示
    $("#my_result").text(barcode);

    // バーコード画像を表示
    $("#my_barcode div").barcode(
        barcode,
        "ean13"
    );

    // カメラを停止
    Quagga.stop();


    // ==============================
    // Python APIへJANコードを送信
    // ==============================

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

        if (data.product_name) {

            $("#product_name").text(
                data.product_name
            );

        } else {

            $("#product_name").text(
                "商品が見つかりません"
            );

        }

    })

    .catch(error => {

        console.error("APIエラー:", error);

        $("#product_name").text(
            "商品検索でエラーが発生しました"
        );

    });

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