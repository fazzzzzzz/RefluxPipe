var option = {
    title: {
        text: '           Reflux Pipe Control System',
        textStyle: {
            color: '#fff'
        }
    },
    series: [{
        type: 'liquidFill',
        data: [0.1 + Math.random() * 20 / 100, 0.15, 0.1, 0.05],
        shape: 'container',
        backgroundStyle: {
            color: 'rgba(0, 0, 0, 0)'
        },
        outline: {
            show: false
        }
    }]
};
$(document).ready(function () {
    var myChart = echarts.init(document.getElementById('login_logo'));
    myChart.setOption(option);
    var animating = false;
    $(".login_submit").click(function () {
        var username = $("#username").val();
        var password = $("#password").val();
        var totp = $("#totp_code").val();
        if (animating) return;
        animating = true;
        $(this).addClass("processing");
        option.series[0].data = [0.98, 0.9, 0.8, 0.7];
        myChart.setOption(option, true);
        $.post("/admin/login", {
            'username': username,
            'password': password,
            'totp': totp,
        }, function (ret) {
            animating = false;
            if (ret === '1') {
                layui.use('layer', function () {
                    var layer = layui.layer;
                    layer.msg('登录成功，欢迎回来～');
                });
                option.series[0].data = [1, 1, 1, 1];
                myChart.setOption(option, true);
                location.reload(true);
            } else {
                option.series[0].data = [0, 0, 0, 0];
                myChart.setOption(option, true);
                layui.use('layer', function () {
                    var layer = layui.layer;
                    layer.msg(ret, {icon: 5});
                });
                $(".login_submit").removeClass("processing");
            }
        })
    });

    $("#signup").click(function () {
        layui.use(['layer', 'form', 'element'], function () {
            var layer = layui.layer, form = layui.form, element = layui.element;
            layer.open({
                type: 1,
                title: false,
                closeBtn: false,
                area: '300px;',
                shade: 0.8,
                id: 'signup_invitecode_window',
                resize: false,
                btn: ['验证', '取消'],
                btnAlign: 'c',
                moveType: 1,
                content:
                    '<div style="padding: 20px; line-height: 22px; background-color: #393D49; color: #fff; font-weight: 600;">' +
                    '   <div class="sign_row">' +
                    '       <svg class="sign_icon svg-icon" viewBox="0 0 20 20">' +
                    '       <path d="M9,10.7c0,0-3,1-3,3.6S8,18,10,18s4-1,4-3.6c0-3.4-3-3.6-3-3.6V3.4h2V2.2h-2V1H9V10.7z"/>' +
                    '       </svg>' +
                    '   <input type="text" class="sign_input" id="sign_invitecode" placeholder="Invite Code" autocomplete="off"/>' +
                    '</div>',
                yes: function (layero, index) {
                    layer.load(2);
                    var invitecode = $("#sign_invitecode").val();
                    $.post("/admin/registe", {
                        'type': 'invite',
                        'invitecode': invitecode
                    }, function (ret) {
                        layer.closeAll('loading');
                        if (ret === '1') {
                            option.series[0].data = [0.8, 0.7, 0.6, 0.5];
                            myChart.setOption(option, true);
                            $('a[class="layui-layer-btn1"]').click();
                            sign_account();
                        } else {
                            option.series[0].data = [0, 0, 0, 0];
                            myChart.setOption(option, true);
                            layer.msg(ret, {icon: 5});
                            $('a[class="layui-layer-btn1"]').click();
                        }
                    });
                },
            })
        })
    });
});

$(document).keypress(function (e) {
    if (e.which === 13) {
        if ($('div[id="signup_invitecode_window"]').length + $('div[id="signup_account_window"]').length + $('div[id="signup_totp_window"]').length <= 0) {
            $('button[type="button"]').click();
        } else {
            $('a[class="layui-layer-btn0"]').click();
        }
    }
});

function sign_account() {
    layui.use(['layer', 'form', 'element'], function () {
        var layer = layui.layer, form = layui.form, element = layui.element;
        layer.open({
            type: 1,
            title: false,
            closeBtn: false,
            area: '300px;',
            shade: 0.8,
            id: 'signup_account_window',
            resize: false,
            btn: ['提交', '取消'],
            btnAlign: 'c',
            moveType: 1,
            content:
                '<div style="padding: 20px; line-height: 22px; background-color: #393D49; color: #fff; font-weight: 600;">' +
                '   <div class="sign_row">' +
                '       <svg class="sign_icon svg-icon" viewBox="0 0 20 20">' +
                '       <path d="M0,20 a10,8 0 0,1 20,0z M10,0 a4,4 0 0,1 0,8 a4,4 0 0,1 0,-8"/>' +
                '       </svg>' +
                '       <input type="text" class="sign_input" id="sign_Username" placeholder="Username" autocomplete="off" onchange="toalias(this.value)"/>' +
                '   </div>' +
                '   <div class="sign_row">' +
                '       <svg class="sign_icon svg-icon" viewBox="0 0 20 20">' +
                '       <path d="M0,20 a10,8 0 0,1 20,0z M10,0 a4,4 0 0,1 0,8 a4,4 0 0,1 0,-8"/>' +
                '       </svg>' +
                '       <input type="text" class="sign_input" id="sign_Alias_Username" placeholder="Username alias" autocomplete="off" onchange="toalias(this.value)"/>' +
                '   </div>' +
                '   <div class="sign_row">' +
                '       <svg class="sign_icon svg-icon" viewBox="0 0 20 20">' +
                '       <path d="M0,20 20,20 20,8 0,8z M10,13 10,16z M4,8 a6,8 0 0,1 12,0"/>' +
                '       </svg>' +
                '       <input type="password" class="sign_input" id="sign_Password" placeholder="Password" autocomplete="off"/>' +
                '   </div>' +
                '   <div class="sign_row">' +
                '       <svg class="sign_icon svg-icon" viewBox="0 0 20 20">' +
                '       <path d="M0,20 20,20 20,8 0,8z M10,13 10,16z M4,8 a6,8 0 0,1 12,0"/>' +
                '       </svg>' +
                '       <input type="password" class="sign_input" id="sign_Password_confirmation" placeholder="Password confirmation" autocomplete="off"/>' +
                '   </div>' +
                '</div>',
            yes: function (layero, index) {
                layer.load(2);
                var myChart = echarts.init(document.getElementById('login_logo'));
                var username = $("#sign_Username").val();
                var alias_username = $("#sign_Alias_Username").val();
                var password = $("#sign_Password").val();
                var password_confirmation = $("#sign_Password_confirmation").val();
                $.post("/admin/registe", {
                    'type': 'account',
                    'username': username,
                    'alias_username': alias_username,
                    'password': password,
                    'password_confirmation': password_confirmation,
                }, function (ret) {
                    layer.closeAll('loading');
                    if (ret.slice(0, 4) === 'totp') {
                        option.series[0].data = [0.9, 0.8, 0.7, 0.6];
                        myChart.setOption(option, true);
                        $('a[class="layui-layer-btn1"]').click();
                        sign_totp(username, ret.slice(5,));
                    } else {
                        option.series[0].data = [0, 0, 0, 0];
                        myChart.setOption(option, true);
                        layer.msg(ret, {icon: 5});
                    }
                });
            },
        });
    });
}

function toalias(username) {
    $("#sign_Alias_Username").val(username.toLowerCase());
}


function sign_totp(username, totp) {
    layui.use(['layer', 'form', 'element'], function () {
        var layer = layui.layer, form = layui.form, element = layui.element;
        layer.open({
            type: 1,
            title: false,
            closeBtn: false,
            area: '300px;',
            shade: 0.8,
            id: 'signup_totp_window',
            resize: false,
            btn: ['注册', '取消'],
            btnAlign: 'c',
            moveType: 1,
            content:
                '<div style="padding: 20px; line-height: 22px; background-color: #393D49; color: #fff; font-weight: 600;">' +
                '   <div class="totp">' +
                '<a>请使用手机TOTP身份验证软件扫描下面的二维码完成二步验证，这也是您以后登陆本系统的安全认证凭证。' +
                '<br>如果您还没有此类软件，请根据手机类型点击按钮，扫码下载下面推荐的TOTP身份验证软件。</a><br>' +
                '<button class="layui-btn layui-btn-primary layui-btn-sm" onclick="msg_url2qr(\'https://sj.qq.com/myapp/detail.htm?apkName=com.google.android.apps.authenticator2\')">Android</button>' +
                '<button class="layui-btn layui-btn-primary layui-btn-sm" onclick="msg_url2qr(\'https://itunes.apple.com/cn/app/google-authenticator/id388497605?mt=8\')">IOS</button>' +
                '<br><br>' +
                '</div>' +
                '   <div id="totp_QRCode"></div>' +
                '   <div class="sign_row">' +
                '       <svg class="sign_icon svg-icon" viewBox="0 0 20 20">' +
                '       <path d="M10,20c4,0,9-3,10-16c-5,0-10-4-10-4S4,4,0,4C1,17,7,20,10,20 M6,10c0,0,2,3,3,3s6-5,6-5"/>' +
                '       </svg>' +
                '       <input type="password" class="sign_input" id="sign_totp_confirmation" placeholder="Totp confirmation" autocomplete="off"/>' +
                '   </div>' +
                '</a>',
            success: function () {
                $('#totp_QRCode').qrcode({width: 128, height: 128, text: totp});
            },
            yes: function (layero, index) {
                layer.load(2);
                var myChart = echarts.init(document.getElementById('login_logo'));
                var totp = $("#sign_totp_confirmation").val();
                $.post("/admin/registe", {
                    'type': 'totp',
                    'totp': totp,
                }, function (ret) {
                    layer.closeAll('loading');
                    if (ret === '1') {
                        option.series[0].data = [1, 0.9, 0.8, 0.7];
                        myChart.setOption(option, true);
                        layer.msg('注册成功，初始化账户可能需要时间，正在跳转～');
                        layer.close();
                        url = '//' + username + document.domain.slice(7,) + ':' + window.location.port + '/admin/';
                        window.location.href = url;
                    } else {
                        option.series[0].data = [0, 0, 0, 0];
                        myChart.setOption(option, true);
                        layer.msg(ret, {icon: 5});
                    }
                });
            }
        });
    })
}

function msg_url2qr(url) {
    layer.msg('<div id="msg_url2qr"></div>', {
        time: 0,
        offset: 'auto',
        btn: ['关闭'],
        shade: 0.8,
        success: function () {
            $('#msg_url2qr').qrcode({width: 256, height: 256, text: url});
        },
    });
}