layui.use(['element', 'form'], function () {
    var element = layui.element,
        form = layui.form;
    $('#submit_useralias').click(function () {
        layer.load(2);
        var useralias = $("#useralias").val();
        var new_useralias = $("#new_useralias").val();
        $.post("/admin/account_setting", {
            'type': 'alias',
            'new_useralias': new_useralias,
        }, function (ret) {
            layer.closeAll('loading');
            if (ret === '1') {
                layer.msg('修改成功！正在跳转～');
                $("#useralias").val(new_useralias);
                url = '//' + new_useralias + document.domain.slice(useralias.length,) + ':' + window.location.port + '/admin/account';
                window.location.href = url;
            } else {
                layer.msg(ret, {icon: 5});
            }
        })

    });
    $('#submit_password').click(function () {
        layer.load(2);
        var password = $("#password").val();
        var new_password = $("#new_password").val();
        var new_password_confirmation = $("#new_password_confirmation").val();
        $.post("/admin/account_setting", {
            'type': 'password',
            'password': password,
            'new_password': new_password,
            'new_password_confirmation': new_password_confirmation
        }, function (ret) {
            layer.closeAll('loading');
            if (ret === '1') {
                layer.msg('修改成功！');
            } else {
                layer.msg(ret, {icon: 5});
            }
        })
    });
});

function toalias(username) {
    $("#new_useralias").val(username.toLowerCase());
}
