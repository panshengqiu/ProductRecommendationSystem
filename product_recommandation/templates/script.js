// 定义一个函数，用于添加商品
function addProduct(img_link, name, price, seller, buy_num) {
    // 创建一个XMLHttpRequest对象
    var xhr = new XMLHttpRequest();
    // 设置请求的方法和url，url中包含查询文本
    xhr.open("GET", "/result?query=" + name);
    // 设置请求的回调函数，当请求完成时执行
    xhr.onload = function() {
        // 如果请求成功，更新页面内容
        if (xhr.status == 200) {
            // 获取响应的文本
            var response = xhr.responseText;
            // 将响应的文本转换为DOM对象
            var parser = new DOMParser();
            var doc = parser.parseFromString(response, "text/html");
            // 获取响应中的all_product元素
            var new_all_product = doc.getElementById("all_product");
            // 获取当前页面的all_product元素
            var old_all_product = document.getElementById("all_product");
            // 用新的all_product元素替换旧的all_product元素
            old_all_product.parentNode.replaceChild(new_all_product, old_all_product);
        }
    };
    // 发送请求
    xhr.send();
}

function shop_page(){
    var recommandation_text = document.getElementById("recommandation_text")
    recommandation_text.innerHTML = "相关店铺售卖商品如下";
}
