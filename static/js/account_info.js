$(document).ready(function () {
    layui.use(['element', 'form'], function () {
        var element = layui.element,
            form = layui.form;
    });
    $("#copy_api_token").click(function () {
        var api_token = $("#api_token");
        api_token.select();
        document.execCommand("Copy");
        layui.use('layer', function () {
            var layer = layui.layer;
            layer.msg('复制成功!');
        });
    });
    $("#update_api_token").click(function () {
        $.post("/admin/api/update_api_token", {}, function (ret) {
            $("#api_token").val(ret);
            layui.use('layer', function () {
                var layer = layui.layer;
                layer.msg('更新成功!');
            });
        })
    });
});


function msg_url2qr(totp) {
    layer.msg('<div id="msg_url2qr"></div>', {
        time: 0,
        offset: 'auto',
        btn: ['关闭'],
        success: function () {
            $('#msg_url2qr').qrcode({width: 256, height: 256, text: totp});
        },
    });
}
