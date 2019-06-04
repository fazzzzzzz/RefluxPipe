# Create your views here.
import datetime
import json
import uuid

import pyotp
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth import logout as session_clear
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Web.models import User, InviteCode, DnsLog, HttpLog


def getRandomStr():
    return str(uuid.uuid1()).replace('-', '')


def escapeHTML(escapeHTML):
    return escapeHTML.replace('<', '&lt;').replace('>', '&gt;').replace('\'', '&#39;').replace('"', '&quot;').replace(
        '&', '&amp;')


def get_useralias(request):
    http_host = request.get_host().split(':')[0]
    if len(http_host.split(".")) <= len(settings.SERVER_DOMAIN.split(".")) or http_host[-1 - len(
            settings.SERVER_DOMAIN):] != "." + settings.SERVER_DOMAIN:
        return ''
    useralias = http_host.split(".")[-1 - len(settings.SERVER_DOMAIN.split('.'))]
    return useralias


def check_host(request):
    useralias = get_useralias(request)
    if User.objects.filter(alias=useralias).count() != 1:
        return False
    else:
        return True


def login(request):
    if check_host(request) is False and get_useralias(request) != 'registe':
        return HttpResponseRedirect('https://www.baidu.com')
    username = request.session.get('username', False)
    if username:
        return HttpResponseRedirect('/admin/')
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username', None)
        if username is None or len(username) <= 0:
            return HttpResponse('请输入用户名!')
        password = request.POST.get('password', None)
        if password is None or len(password) <= 0:
            return HttpResponse('请输入密码!')
        totp = request.POST.get('totp', None)
        if totp is None or len(totp) != 6:
            return HttpResponse('请正确输入6位TOTP令牌口令!')
        account = User.objects.filter(username=username, password=password)
        if account.count() != 1:
            return HttpResponse('登陆失败，请稍后重试!')
        if get_useralias(request) != account.first().alias:
            return HttpResponse('登陆失败，请稍后重试!')
        if pyotp.TOTP(account.first().totp).verify(totp) is False:
            return HttpResponse('登陆失败，请稍后重试!')
        request.session['username'] = username
        request.session['useralias'] = account.first().alias
        return HttpResponse('1')
    else:
        return HttpResponse('')


def registe(request):
    if get_useralias(request) != 'registe':
        return HttpResponseRedirect('https://www.baidu.com')
    username = request.session.get('username', False)
    if username:
        del request.session['username']
    if request.method != 'POST':
        return HttpResponse('')
    type = request.POST.get('type', None)
    if type is None or len(type) <= 0:
        return HttpResponse('验证失败!')
    if type == 'invite':
        invitecode = request.POST.get('invitecode', None)
        if invitecode == 'admin':
            if User.objects.filter(is_admin=True).count() == 0:
                request.session['invitecode'] = invitecode
                return HttpResponse('1')
        if invitecode is None or len(invitecode) < 16:
            return HttpResponse('请输入16位邀请码!')
        if InviteCode.objects.filter(code=invitecode, status=True).count() != 1:
            return HttpResponse('请输入有效的邀请码!')
        request.session['invitecode'] = invitecode
        return HttpResponse('1')
    elif type == 'account':
        invitecode = request.session.get('invitecode', None)
        if invitecode is None:
            return HttpResponse('邀请码错误,请刷新页面重试!')
        username = request.POST.get('username', None)
        if username is None or len(username) <= 0:
            return HttpResponse('请输入用户名!')
        alias_username = request.POST.get('alias_username', None)
        if alias_username is None or len(alias_username) <= 0:
            return HttpResponse('请输入别名!')
        if alias_username.islower() is False:
            return HttpResponse('别名仅支持小写字母!')
        password = request.POST.get('password', None)
        if password is None or len(password) <= 0:
            return HttpResponse('请输入密码!')
        password_confirmation = request.POST.get('password_confirmation', None)
        if password_confirmation is None or len(password_confirmation) <= 0:
            return HttpResponse('请输入验证密码!')
        if password != password_confirmation:
            return HttpResponse('两次输入的密码不一致!')
        if User.objects.filter(username=username).count() == 1:
            return HttpResponse('用户名已存在!')
        if User.objects.filter(alias=alias_username).count() == 1 or alias_username == 'registe':
            return HttpResponse('用户别名已存在!')
        totp = pyotp.random_base32()
        account_config = {
            'username': username,
            'alias_username': alias_username,
            'password': password,
            'totp': totp,
            'invitecode': invitecode
        }
        if invitecode == 'admin':
            account_config['is_admin'] = True
        else:
            account_config['is_admin'] = False
        del request.session['invitecode']
        request.session['account_config'] = account_config
        return HttpResponse('totp:' + pyotp.totp.TOTP(totp).provisioning_uri(username, issuer_name="RefluxPipe"))
    elif type == 'totp':
        account_config = request.session.get('account_config', None)
        if account_config is None:
            return HttpResponse('注册失败,请刷新页面重试!')
        totp = request.POST.get('totp', None)
        if totp is None or len(totp) != 6:
            return HttpResponse('请正确输入6位TOTP令牌口令!')
        if pyotp.TOTP(account_config['totp']).verify(totp) is False:
            return HttpResponse('登陆失败，请稍后重试!')
        del request.session['account_config']
        User.objects.create(
            username=account_config['username'],
            alias=account_config['alias_username'],
            password=account_config['password'],
            totp=account_config['totp'],
            api_token=getRandomStr(),
            is_admin=account_config['is_admin']
        )
        InviteCode.objects.filter(code=account_config['invitecode']).update(status=False)
        request.session['username'] = account_config['username']
        request.session['useralias'] = account_config['alias_username']
        return HttpResponse('1')
    else:
        return HttpResponse('')


def index(request):
    username = request.session.get('username', False)
    if username is False:
        return HttpResponseRedirect('/admin/login')
    if get_useralias(request) != request.session.get('useralias', False):
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'GET':
        vardict = {
            'username': username,
            'api_token': User.objects.filter(username=username)[0].api_token,
            'is_admin': User.objects.filter(username=username)[0].is_admin,
            'host': request.headers["host"],
            'domain': get_useralias(request) + "." + settings.SERVER_DOMAIN
        }
        nowtime = datetime.datetime.now()
        vardict['dns_7'] = DnsLog.objects.filter(username=username,
                                                 logtime__range=(nowtime - datetime.timedelta(days=1), nowtime)).count()
        vardict['dns_6'] = DnsLog.objects.filter(username=username,
                                                 logtime__range=(nowtime - datetime.timedelta(days=2),
                                                                 nowtime - datetime.timedelta(days=1))).count()
        vardict['dns_5'] = DnsLog.objects.filter(username=username,
                                                 logtime__range=(nowtime - datetime.timedelta(days=3),
                                                                 nowtime - datetime.timedelta(days=2))).count()
        vardict['dns_4'] = DnsLog.objects.filter(username=username,
                                                 logtime__range=(nowtime - datetime.timedelta(days=4),
                                                                 nowtime - datetime.timedelta(days=3))).count()
        vardict['dns_3'] = DnsLog.objects.filter(username=username,
                                                 logtime__range=(nowtime - datetime.timedelta(days=5),
                                                                 nowtime - datetime.timedelta(days=4))).count()
        vardict['dns_2'] = DnsLog.objects.filter(username=username,
                                                 logtime__range=(nowtime - datetime.timedelta(days=6),
                                                                 nowtime - datetime.timedelta(days=5))).count()
        vardict['dns_1'] = DnsLog.objects.filter(username=username,
                                                 logtime__range=(nowtime - datetime.timedelta(days=7),
                                                                 nowtime - datetime.timedelta(days=6))).count()
        vardict['http_7'] = HttpLog.objects.filter(username=username,
                                                   logtime__range=(
                                                   nowtime - datetime.timedelta(days=1), nowtime)).count()
        vardict['http_6'] = HttpLog.objects.filter(username=username,
                                                   logtime__range=(nowtime - datetime.timedelta(days=2),
                                                                   nowtime - datetime.timedelta(days=1))).count()
        vardict['http_5'] = HttpLog.objects.filter(username=username,
                                                   logtime__range=(nowtime - datetime.timedelta(days=3),
                                                                   nowtime - datetime.timedelta(days=2))).count()
        vardict['http_4'] = HttpLog.objects.filter(username=username,
                                                   logtime__range=(nowtime - datetime.timedelta(days=4),
                                                                   nowtime - datetime.timedelta(days=3))).count()
        vardict['http_3'] = HttpLog.objects.filter(username=username,
                                                   logtime__range=(nowtime - datetime.timedelta(days=5),
                                                                   nowtime - datetime.timedelta(days=4))).count()
        vardict['http_2'] = HttpLog.objects.filter(username=username,
                                                   logtime__range=(nowtime - datetime.timedelta(days=6),
                                                                   nowtime - datetime.timedelta(days=5))).count()
        vardict['http_1'] = HttpLog.objects.filter(username=username,
                                                   logtime__range=(nowtime - datetime.timedelta(days=7),
                                                                   nowtime - datetime.timedelta(days=6))).count()
        return render(request, 'index.html', vardict)
    else:
        return HttpResponse('')


def account_info(request):
    username = request.session.get('username', False)
    useralias = request.session.get('useralias', False)
    if username is False or get_useralias(request) != useralias:
        return HttpResponseRedirect('https://www.baidu.com')
    user = User.objects.filter(username=username)[0]
    if request.method == 'GET':
        vardict = {
            'username': username,
            'useralias': useralias,
            'totp': pyotp.totp.TOTP(user.totp).provisioning_uri(username, issuer_name="RefluxPipe"),
            'api_token': user.api_token,
            'is_admin': user.is_admin
        }
        return render(request, 'account_info.html', vardict)
    else:
        return HttpResponse('')


def account_setting(request):
    username = request.session.get('username', False)
    useralias = request.session.get('useralias', False)
    if username is False or get_useralias(request) != useralias:
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'GET':
        vardict = {
            'username': username,
            'useralias': useralias,
            'is_admin': User.objects.filter(username=username)[0].is_admin
        }
        return render(request, 'account_setting.html', vardict)
    elif request.method == 'POST':
        type = request.POST.get('type', None)
        if type == 'alias':
            new_useralias = request.POST.get('new_useralias', None)
            if new_useralias is None or len(new_useralias) <= 0:
                return HttpResponse('请输入别名!')
            if new_useralias.islower() is False:
                return HttpResponse('别名仅支持小写字母!')
            if useralias == new_useralias:
                return HttpResponse('当前别名与新别名一致!')
            if User.objects.filter(alias=new_useralias).count() == 1 or new_useralias == 'registe':
                return HttpResponse('用户别名已存在!')
            User.objects.filter(username=username).update(alias=new_useralias)
            request.session['useralias'] = new_useralias
            return HttpResponse('1')
        elif type == 'password':
            password = request.POST.get('password', None)
            if password is None or len(password) <= 0:
                return HttpResponse('请输入旧密码!')
            new_password = request.POST.get('new_password', None)
            if new_password is None or len(new_password) <= 0:
                return HttpResponse('请输入新密码!')
            new_password_confirmation = request.POST.get('new_password_confirmation', None)
            if new_password_confirmation is None or len(new_password_confirmation) <= 0:
                return HttpResponse('请输入验证密码!')
            if new_password != new_password_confirmation:
                return HttpResponse('两次输入的密码不一致!')
            account = User.objects.filter(username=username, password=password)
            if account.count() != 1:
                return HttpResponse('旧密码错误!')
            account.update(password=new_password)
            return HttpResponse('1')
    else:
        return HttpResponse('')


def update_api_token(request):
    username = request.session.get('username', False)
    useralias = request.session.get('useralias', False)
    if username is False or get_useralias(request) != useralias:
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'POST':
        api_token = getRandomStr()
        User.objects.filter(username=username).update(api_token=api_token)
        return HttpResponse(api_token)
    else:
        return HttpResponse('')


def admin_setting(request):
    username = request.session.get('username', False)
    useralias = request.session.get('useralias', False)
    if username is False or get_useralias(request) != useralias:
        return HttpResponseRedirect('https://www.baidu.com')
    if User.objects.filter(username=username, is_admin=True).count() != 1:
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'GET':
        vardict = {
            'username': username
        }
        return render(request, 'admin_setting.html', vardict)
    else:
        return HttpResponse('')


def dnslog(request):
    username = request.session.get('username', False)
    if username is False or get_useralias(request) != request.session.get('useralias', False):
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'GET':
        vardict = {
            'username': username,
            'is_admin': User.objects.filter(username=username)[0].is_admin
        }
        return render(request, 'dnslog.html', vardict)
    else:
        return HttpResponse('')


def httplog(request):
    username = request.session.get('username', False)
    if username is False or get_useralias(request) != request.session.get('useralias', False):
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'GET':
        vardict = {
            'username': username,
            'is_admin': User.objects.filter(username=username)[0].is_admin
        }
        return render(request, 'httplog.html', vardict)
    else:
        return HttpResponse('')


def getTableDnslog(request):
    username = request.session.get('username', False)
    if username is False or get_useralias(request) != request.session.get('useralias', False):
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'POST':
        page = request.POST.get('page', None)
        if page is None or len(page) <= 0:
            return HttpResponse('请输入页码!')
        limit = request.POST.get('limit', None)
        if limit is None or len(limit) <= 0:
            return HttpResponse('请输入页数!')
        table_dnslog = DnsLog.objects.filter(username=username).order_by("-id")
        result = {
            "code": 0,
            "msg": "",
            "count": table_dnslog.count(),
            "data": []
        }
        for i in table_dnslog[(int(page) - 1) * (int(limit)):int(page) * int(limit)]:
            result['data'].append({
                'id': i.id,
                'username': escapeHTML(i.username),
                'domain': escapeHTML(i.domain),
                'host': escapeHTML(i.host),
                'type': escapeHTML(i.type),
                'logtime': datetime.datetime.fromtimestamp(i.logtime.timestamp() + 8 * 60 * 60).strftime(
                    "%Y/%m/%d %H:%M:%S")
            })
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('')


def delDnslog(request):
    username = request.session.get('username', False)
    if username is False or get_useralias(request) != request.session.get('useralias', False):
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'POST':
        type = request.POST.get('type', None)
        if type == 'delselect':
            idlist = request.POST.get('idlist', None)
            if idlist is None or len(idlist) <= 0:
                return HttpResponse('请求id不存在!')
            idlist = idlist.split(',')
            for i in idlist:
                if DnsLog.objects.filter(id=i, username=username).count() != 1:
                    return HttpResponse('请求id不存在!')
            for i in idlist:
                DnsLog.objects.filter(id=i, username=username).delete()
            return HttpResponse('1')
        elif type == 'delall':
            DnsLog.objects.filter(username=username).delete()
            return HttpResponse('1')
        else:
            return HttpResponse('请求类型错误!')
    else:
        return HttpResponse('')


def getTableUser(request):
    username = request.session.get('username', False)
    if username is False or get_useralias(request) != request.session.get('useralias', False):
        return HttpResponseRedirect('https://www.baidu.com')
    if User.objects.filter(username=username, is_admin=True).count() != 1:
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'POST':
        page = request.POST.get('page', None)
        if page is None or len(page) <= 0:
            return HttpResponse('请输入页码!')
        limit = request.POST.get('limit', None)
        if limit is None or len(limit) <= 0:
            return HttpResponse('请输入页数!')
        table_user = User.objects.filter().order_by("id")
        result = {
            "code": 0,
            "msg": "",
            "count": table_user.count(),
            "data": []
        }
        for i in table_user[(int(page) - 1) * (int(limit)):int(page) * int(limit)]:
            result['data'].append({
                'id': i.id,
                'username': escapeHTML(i.username),
                'alias': i.alias,
                'is_admin': '是' if i.is_admin is True else '否',
            })
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('')


def delUser(request):
    username = request.session.get('username', False)
    if username is False or get_useralias(request) != request.session.get('useralias', False):
        return HttpResponseRedirect('https://www.baidu.com')
    if User.objects.filter(username=username, is_admin=True).count() != 1:
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'POST':
        idlist = request.POST.get('idlist', None)
        if idlist is None or len(idlist) <= 0:
            return HttpResponse('请求id不存在!')
        idlist = idlist.split(',')
        for i in idlist:
            if User.objects.filter(id=i).count() != 1:
                return HttpResponse('请求id不存在!')
            if User.objects.filter(id=i)[0].is_admin is True:
                return HttpResponse('无法删除管理员!')
        for i in idlist:
            User.objects.filter(id=i).delete()
        return HttpResponse('1')
    else:
        return HttpResponse('')


def getTableInviteCode(request):
    username = request.session.get('username', False)
    if username is False or get_useralias(request) != request.session.get('useralias', False):
        return HttpResponseRedirect('https://www.baidu.com')
    if User.objects.filter(username=username, is_admin=True).count() != 1:
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'POST':
        page = request.POST.get('page', None)
        if page is None or len(page) <= 0:
            return HttpResponse('请输入页码!')
        limit = request.POST.get('limit', None)
        if limit is None or len(limit) <= 0:
            return HttpResponse('请输入页数!')
        table_invite_code = InviteCode.objects.filter().order_by("id")
        result = {
            "code": 0,
            "msg": "",
            "count": table_invite_code.count(),
            "data": []
        }
        for i in table_invite_code[(int(page) - 1) * (int(limit)):int(page) * int(limit)]:
            result['data'].append({
                'id': i.id,
                'code': i.code,
                'status': '未使用' if i.status is True else '已使用',
            })
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('')


def delInviteCode(request):
    username = request.session.get('username', False)
    if username is False or get_useralias(request) != request.session.get('useralias', False):
        return HttpResponseRedirect('https://www.baidu.com')
    if User.objects.filter(username=username, is_admin=True).count() != 1:
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'POST':
        type = request.POST.get('type', None)
        if type == 'delselect':
            idlist = request.POST.get('idlist', None)
            if idlist is None or len(idlist) <= 0:
                return HttpResponse('请求id不存在!')
            idlist = idlist.split(',')
            for i in idlist:
                if InviteCode.objects.filter(id=i).count() != 1:
                    return HttpResponse('请求id不存在!')
            for i in idlist:
                InviteCode.objects.filter(id=i).delete()
            return HttpResponse('1')
        elif type == 'delall':
            InviteCode.objects.filter().delete()
            return HttpResponse('1')
        else:
            return HttpResponse('请求类型错误!')
    else:
        return HttpResponse('')


def createInviteCode(request):
    username = request.session.get('username', False)
    if username is False or get_useralias(request) != request.session.get('useralias', False):
        return HttpResponseRedirect('https://www.baidu.com')
    if User.objects.filter(username=username, is_admin=True).count() != 1:
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'POST':
        count = int(request.POST.get('count', None))
        if count <= 0 or count > 100:
            return HttpResponse('必须为1-100的整数！')
        for i in range(count):
            InviteCode.objects.create(code=getRandomStr(), status=True)
        return HttpResponse('1')
    else:
        return HttpResponse('')


def getTableHttplog(request):
    username = request.session.get('username', False)
    if username is False or get_useralias(request) != request.session.get('useralias', False):
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'POST':
        page = request.POST.get('page', None)
        if page is None or len(page) <= 0:
            return HttpResponse('请输入页码!')
        limit = request.POST.get('limit', None)
        if limit is None or len(limit) <= 0:
            return HttpResponse('请输入页数!')
        table_httplog = HttpLog.objects.filter(username=username).order_by("-id")
        result = {
            "code": 0,
            "msg": "",
            "count": table_httplog.count(),
            "data": []
        }
        for i in table_httplog[(int(page) - 1) * (int(limit)):int(page) * int(limit)]:
            result['data'].append({
                'id': i.id,
                'username': escapeHTML(i.username),
                'host': escapeHTML(i.host),
                'url': escapeHTML(i.url),
                'method': escapeHTML(i.method),
                'useragent': escapeHTML(i.useragent),
                'body': escapeHTML(i.body),
                'contenttype': escapeHTML(i.contenttype),
                'referer': escapeHTML(i.referer),
                'logtime': datetime.datetime.fromtimestamp(i.logtime.timestamp() + 8 * 60 * 60).strftime(
                    "%Y/%m/%d %H:%M:%S")
            })
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('')


def delHttplog(request):
    username = request.session.get('username', False)
    if username is False or get_useralias(request) != request.session.get('useralias', False):
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'POST':
        type = request.POST.get('type', None)
        if type == 'delselect':
            idlist = request.POST.get('idlist', None)
            if idlist is None or len(idlist) <= 0:
                return HttpResponse('请求id不存在!')
            idlist = idlist.split(',')
            for i in idlist:
                if HttpLog.objects.filter(id=i, username=username).count() != 1:
                    return HttpResponse('请求id不存在!')
            for i in idlist:
                HttpLog.objects.filter(id=i, username=username).delete()
            return HttpResponse('1')
        elif type == 'delall':
            HttpLog.objects.filter(username=username).delete()
            return HttpResponse('1')
        else:
            return HttpResponse('请求类型错误!')
    else:
        return HttpResponse('')


def logout(request):
    username = request.session.get('username', False)
    session_clear(request)
    if username is False or get_useralias(request) != request.session.get('useralias', False):
        return HttpResponseRedirect('https://www.baidu.com')
    return HttpResponseRedirect('/admin/')


@csrf_exempt
def recordhttplog(request):
    response = HttpResponse('')
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, PUT"
    response["Access-Control-Allow-Headers"] = "Accept, Cookie, x-requested-with, content-type, Token, Origin"
    if check_host(request):
        HttpLog.objects.create(
            username=User.objects.filter(alias=get_useralias(request)).first().username,
            host=request.META['REMOTE_ADDR'],
            url=request.get_full_path(),
            method=request.method,
            useragent=request.META.get('HTTP_USER_AGENT', ''),
            body=request.body.decode(),
            contenttype=request.content_type,
            referer=request.META.get('HTTP_REFERER', '')
        )
        async_to_sync(get_channel_layer().group_send)(
            'group_%s' % User.objects.filter(alias=get_useralias(request)).first().username,
            {
                'type': 'client_message',
                'message': 'httplog_update'
            }
        )
    return response


@csrf_exempt
def queryapi(request):
    if check_host(request):
        return HttpResponseRedirect('https://www.baidu.com')
    if request.method == 'get':
        type = request.POST.get('type', None)
        if type is None or len(type) <= 0:
            return HttpResponse('查询类型不能为空!')
        query = request.POST.get('query', None)
        if query is None or len(query) <= 0:
            return HttpResponse('查询内容不能为空!')
        api = request.POST.get('api', None)
        if api is None or len(api) <= 0:
            return HttpResponse('api不能为空!')
        username = User.objects.filter(alias=get_useralias(request))[0].username
        if User.objects.filter(username=username, api_token=api).count != 0:
            return HttpResponse('api验证失败')
        if type == 'dns':
            if DnsLog.objects.filter(username=username, domain=query).count != 0:
                return HttpResponse('True')
            else:
                return HttpResponse('False')
        elif type == 'http':
            if HttpLog.objects.filter(username=username, url=query).count() != 0:
                return HttpResponse('True')
            else:
                return HttpResponse('False')
        else:
            return HttpResponse('不支持的查询类型!')
    else:
        return HttpResponse('')
