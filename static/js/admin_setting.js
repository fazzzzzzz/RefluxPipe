$(document).ready(function () {
    layui.use(['element', 'form', 'table'], function () {
        var element = layui.element,
            form = layui.form;
        table = layui.table;
        table.render({
            elem: '#user_table',
            url: '/admin/api/table/user',
            method: 'POST',
            defaultToolbar: ['filter', 'exports', 'print'],
            page: true,
            loading: true,
            title: 'dnslog',
            cols: [[
                {type: 'checkbox'},
                {field: 'id', width: '10%', title: 'ID', sort: true},
                {field: 'username', width: '30%', title: '用户名', sort: true},
                {field: 'alias', width: '30%', title: '别名', sort: true},
                {field: 'is_admin', width: '15%', title: '管理员', sort: true},
                {field: 'right', width: '15%', title: '操作', toolbar: '#user_fieldbar'},
            ]],
            done: function () {
                $("[data-field='username'] .layui-table-cell").each(function () {
                    $(this).text(unescapeHTML($(this).text()))
                });
            }
        });
        table.on('tool(user_table)', function (obj) {
            var data = obj.data;
            if (obj.event === 'del') {
                layer.load(2);
                $.post("/admin/api/table/user/del", {
                        'idlist': JSON.stringify(obj.data["id"]),
                    }, function (ret) {
                        layer.closeAll('loading');
                        if (ret === '1') {
                            layer.msg('删除成功!');
                            obj.del();
                        } else {
                            layer.msg(ret, {icon: 5});
                        }
                    }
                )
            }
        });
        table.render({
            elem: '#invite_code_table',
            url: '/admin/api/table/invite_code',
            method: 'POST',
            toolbar: '#toolbar',
            defaultToolbar: ['filter', 'exports', 'print'],
            page: true,
            loading: true,
            title: 'dnslog',
            cols: [[
                {type: 'checkbox'},
                {field: 'id', width: '10%', title: 'ID', sort: true},
                {field: 'code', width: '40%', title: '邀请码', sort: true},
                {field: 'status', width: '30%', title: '状态', sort: true},
                {field: 'right', width: '20%', title: '操作', toolbar: '#invite_code_fieldbar'},
            ]],
        });
        var invite_code_create_count = 0;
        table.on('toolbar(invite_code_table)', function (obj) {
            var checkStatus = table.checkStatus(obj.config.id);
            switch (obj.event) {
                case 'delselect':
                    var data = checkStatus.data;
                    for (i in data) {
                        if (i === '0') {
                            idlist = (JSON.stringify(data[i]['id']));
                        } else {
                            idlist += ',' + (JSON.stringify(data[i]['id']));
                        }

                    }
                    if (data.length === 0) {
                        layer.msg('您还没选中需要删除的记录!');
                    } else {
                        layer.load(2);
                        $.post("/admin/api/table/invite_code/del", {
                            'type': 'delselect',
                            'idlist': idlist,
                        }, function (ret) {
                            layer.closeAll('loading');
                            if (ret === '1') {
                                layer.msg('删除成功！共删除' + data.length + '项');
                                table.reload('invite_code_table')
                            } else {
                                layer.msg(ret, {icon: 5});
                            }
                        })
                    }
                    break;
                case 'delall':
                    layer.load(2);
                    $.post("/admin/api/table/invite_code/del", {
                        'type': 'delall',
                    }, function (ret) {
                        layer.closeAll('loading');
                        if (ret === '1') {
                            layer.msg('邀请码已清空！');
                            table.reload('invite_code_table')
                        } else {
                            layer.msg(ret, {icon: 5});
                        }
                    });
                    break;
                case 'create':
                    layui.use(['layer', 'form', 'element'], function () {
                        var layer = layui.layer,
                            form = layui.form,
                            element = layui.element;
                        layer.open({
                            type: 1,
                            title: false,
                            closeBtn: false,
                            area: '300px;',
                            shade: 0.8,
                            id: 'create_invitecode_window',
                            resize: false,
                            btn: ['生成', '取消'],
                            btnAlign: 'c',
                            moveType: 1,
                            content:
                                '<div style="margin-top:20px;margin-left:20px;margin-right:20px;">' +
                                '<p style="margin-bottom: 20px;">生成数量:</p>' +
                                '</fieldset>' +
                                '<div id="slide" class="demo-slider"></div>' +
                                '<fieldset class="layui-elem-field layui-field-title" style="margin-top: 30px;">' +
                                '</div>',
                            yes:
                                function (layero, index) {
                                    layer.load(2);
                                    var invitecode = $("#sign_invitecode").val();
                                    $.post("/admin/api/table/invite_code/create", {
                                        'count': invite_code_create_count,
                                    }, function (ret) {
                                        layer.closeAll('loading');
                                        if (ret === '1') {
                                            layer.msg('邀请码生成成功！');
                                            table.reload('invite_code_table');
                                            $('a[class="layui-layer-btn1"]').click();
                                        } else {
                                            layer.msg(ret, {icon: 5});
                                        }
                                    });
                                },
                            success:
                                function (layero, index) {
                                    layui.use('slider', function () {
                                        var $ = layui.$,
                                            slider = layui.slider;
                                        slider.render({
                                            elem: '#slide',
                                            input: true,
                                            change: function (value) {
                                                invite_code_create_count = value
                                            }
                                        })
                                    })
                                }
                        })
                    });
                    break;
            }
        });
        table.on('tool(invite_code_table)', function (obj) {
            var data = obj.data;
            if (obj.event === 'del') {
                layer.load(2);
                $.post("/admin/api/table/invite_code/del", {
                        'type': 'delselect',
                        'idlist': JSON.stringify(obj.data["id"]),
                    }, function (ret) {
                        layer.closeAll('loading');
                        if (ret === '1') {
                            layer.msg('删除成功!');
                            obj.del();
                        } else {
                            layer.msg(ret, {icon: 5});
                        }
                    }
                )
            }
        })
    });
});

function unescapeHTML(unescapeHTML) {
    unescapeHTML = "" + unescapeHTML;
    return unescapeHTML.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;/g, "'");
}
