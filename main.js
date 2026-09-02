console.log("main.js!!");

$(document).ready(() => {

    console.log("Ready!!");

    // バーコードをすでに読み込んだか
    let detected = false;

    // カメラが起動中か
    let cameraRunning = false;


    // =========================
    // Startボタン
    // =========================
    $("#my_start").click(() => {

        console.log("Start!!");

        // すでに起動している場合
        if (cameraRunning) {
            console.log("カメラはすでに起動しています");
            return;
        }

        // カメラ表示
        $("#my_quagga").css("visibility", "visible");

        // 新しくバーコードを読み込めるようにする
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

        }, (err) => {

            if (err) {

                console.error("Quagga初期化エラー:", err);

                cameraRunning = false;

                return;
            }

            console.log("Initialization finished!!");

            Quagga.start();

            cameraRunning = true;
        });
    });


    // =========================
    // Stopボタン
    // =========================
    $("#my_stop").click(() => {

        console.log("Stop!!");

        if (cameraRunning) {

            Quagga.stop();

            cameraRunning = false;
        }

        detected = false;
    });


    // =========================
    // バーコード読み取り
    // =========================
    Quagga.onDetected((result) => {

        // すでに読み込んでいたら何もしない
        if (detected) {
            return;
        }

        const barcode = result.codeResult.code;

        console.log("読み取ったバーコード:", barcode);


        // =========================
        // 490から始まるバーコードだけ許可
        // =========================
        if (!barcode.startsWith("490")) {

            console.log(
                "490以外のバーコードなので無視します:",
                barcode
            );

            return;
        }


        // 490から始まる場合だけ読み取り完了
        detected = true;

        console.log(
            "490から始まるバーコードを検出:",
            barcode
        );


        // カメラ停止
        if (cameraRunning) {

            Quagga.stop();

            cameraRunning = false;
        }


        // 商品検索
        searchProduct(barcode);

    });


    // =========================
    // 商品検索ボタン
    // =========================
    $("#barcode_search").click(() => {

        console.log("商品検索ボタンが押されました");

        const barcode = $("#barcode_input").val().trim();

        console.log("入力されたバーコード:", barcode);


        // 13桁チェック
        if (!/^\d{13}$/.test(barcode)) {

            alert("13桁のJANコードを入力してください");

            return;
        }


        // カメラが起動中なら停止
        if (cameraRunning) {

            console.log(
                "テキスト検索のためカメラを停止します"
            );

            Quagga.stop();

            cameraRunning = false;
        }

        detected = false;


        // 商品検索
        searchProduct(barcode);

    });


    // =========================
    // Enterキーで商品検索
    // =========================
    $("#barcode_input").keypress((event) => {

        if (event.key === "Enter") {

            $("#barcode_search").click();
        }

    });


    // =========================
    // 商品検索処理
    // =========================
    function searchProduct(barcode) {

        console.log("商品検索:", barcode);


        // JANコード表示
        $("#my_result").text(barcode);


        fetch("/api/search", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                barcode: barcode
            })

        })

        .then((response) => {

            console.log(
                "APIステータス:",
                response.status
            );

            return response.json();

        })

        .then((data) => {

            console.log(
                "APIからの返答:",
                data
            );


            // =========================
            // 商品名
            // =========================
            if (data.product_name) {

                $("#product_name").text(
                    data.product_name
                );

            } else {

                $("#product_name").text(
                    "商品が見つかりません"
                );
            }


            // =========================
            // バーコード画像
            // =========================
            if (data.barcode_image) {

                $("#my_barcode").html(
                    `<img src="${data.barcode_image}" alt="バーコード画像">`
                );

            } else {

                $("#my_barcode").html(
                    "<div>バーコード画像を生成できませんでした</div>"
                );
            }


            // カメラを隠す
            // display:noneにはしない
            $("#my_quagga").css(
                "visibility",
                "hidden"
            );

        })

        .catch((error) => {

            console.error(
                "APIエラー:",
                error
            );

            $("#product_name").text(
                "商品検索でエラーが発生しました"
            );

        });

    }

});