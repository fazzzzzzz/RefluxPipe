layui.use(['element', 'form', 'table'], function () {
    var element = layui.element,
        form = layui.form,
        table = layui.table;
    var ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    var Socket = new WebSocket(ws_scheme + '://' + window.location.host + "/ws/");
    Socket.onmessage = function (e) {
        var data = JSON.parse(e.data);
        var message = data['message'];
        if (message === 'dnslog_update') {
            table.reload('dnslog_table')
        }
    };
    table.render({
        elem: '#dnslog_table',
        url: '/admin/api/table/dnslog',
        method: 'POST',
        toolbar: '#toolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        page: true,
        loading: true,
        title: 'dnslog',
        cols: [[
            {type: 'checkbox'},
            {field: 'id', width: '5%', title: 'ID', sort: true},
            {field: 'username', width: '10%', title: '用户名', sort: true},
            {field: 'domain', width: '30%', title: '请求域名', sort: true},
            {field: 'host', width: '10%', title: 'IP', sort: true},
            {field: 'type', width: '10%', title: '类型', sort: true},
            {field: 'logtime', width: '25%', title: '时间', sort: true},
            {field: 'right', width: '7%', title: '操作', toolbar: '#fieldbar'},
        ]],
        done: function () {
            $("[data-field='username'] .layui-table-cell").each(function () {
                $(this).text(unescapeHTML($(this).text()))
            });
            $("[data-field='domain'] .layui-table-cell").each(function () {
                $(this).text(unescapeHTML($(this).text()))
            });
            $("[data-field='host'] .layui-table-cell").each(function () {
                $(this).text(unescapeHTML($(this).text()))
            });
        }
    });
    table.on('toolbar(dnslog_table)', function (obj) {
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
                    $.post("/admin/api/table/dnslog/del", {
                        'type': 'delselect',
                        'idlist': idlist,
                    }, function (ret) {
                        layer.closeAll('loading');
                        if (ret === '1') {
                            layer.msg('删除成功！共删除' + data.length + '项');
                            table.reload('dnslog_table')
                        } else {
                            layer.msg(ret, {icon: 5});
                        }
                    })
                }
                break;
            case 'delall':
                layer.load(2);
                $.post("/admin/api/table/dnslog/del", {
                    'type': 'delall',
                }, function (ret) {
                    layer.closeAll('loading');
                    if (ret === '1') {
                        layer.msg('您的记录已清空！');
                        table.reload('dnslog_table')
                    } else {
                        layer.msg(ret, {icon: 5});
                    }
                });
                break;
        }
    });
    table.on('tool(dnslog_table)', function (obj) {
        var data = obj.data;
        if (obj.event === 'del') {
            layer.load(2);
            $.post("/admin/api/table/dnslog/del", {
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


function unescapeHTML(unescapeHTML) {
    unescapeHTML = "" + unescapeHTML;
    return unescapeHTML.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;/g, "'");
}