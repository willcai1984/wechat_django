# -*- coding: utf-8 -*-
import hashlib
import django.utils.timezone as timezone

from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.http import JsonResponse
from .models import Account
from .models import User
from .models import AccountDetail
from .models import AccountPay
from .util import WechatLogin, check_account_renren
from .pay_setting import *
from django.http import HttpResponseRedirect

user_status_dict = {
    0: "待抓取",
    1: "抓取中",
    2: "抓取成功",
    3: "抓取失败"
}


def account_add(request):
    if request.method == 'POST':
        user_name = request.POST['user_name']
        user_pwd = request.POST['user_pwd']
        open_id = request.POST['user_id']
        users = User.objects.filter(is_delete=0).filter(open_id=open_id)
        if Account.objects.filter(is_delete=0).filter(open_id=open_id).filter(user_name=user_name).count() == 0:
            Account.objects.create(
                open_id=open_id,
                user_name=user_name,
                user_pwd=user_pwd
            )
        accounts = Account.objects.filter(is_delete=0).filter(open_id=open_id)
        context = {'user': users[0].nick_name.encode('iso8859-1').decode('utf-8'),
                   'open_id': open_id,
                   'img_url': users[0].img_url,
                   'account_list': accounts}
        return render(request, '0home_list.html', context)


def account_update(request):
    if request.method == 'POST':
        user_name = request.POST['user_name']
        user_pwd = request.POST['user_pwd']
        open_id = request.POST['user_id']
        users = User.objects.filter(is_delete=0).filter(open_id=open_id)
        account = Account.objects.filter(is_delete=0).filter(open_id=open_id).get(user_name=user_name)
        account.user_pwd = user_pwd
        account.save()
        accounts = Account.objects.filter(is_delete=0).filter(open_id=open_id)
        context = {'user': users[0].nick_name.encode('iso8859-1').decode('utf-8'),
                   'open_id': open_id,
                   'img_url': users[0].img_url,
                   'account_list': accounts}
        return render(request, '0home_list.html', context)


def account_check(request):
    if request.method == 'GET':
        user_name = request.GET['user_name']
        user_pwd = request.GET['user_pwd']
        open_id = request.GET['user_id']
        accounts = Account.objects.filter(is_delete=0).filter(open_id=open_id)
        for account in accounts:
            if account.user_name == user_name:
                return JsonResponse({'status': False, 'msg': '此账号已存在现有列表中'})
        is_pass = check_account_renren(user_name, user_pwd)
        if is_pass:
            result = {'status': True, 'msg': '人人网登录验证成功'}
        else:
            result = {'status': False, 'msg': '用户名密码错误'}
        return JsonResponse(result)


def pay_result(request):
    if request.method == 'GET':
        pay_no = request.GET['pay_no']
        pay_results = AccountPay.objects.filter(is_delete=0).filter(pay_no=pay_no)
        if pay_results.count() == 0:
            return HttpResponse("无对应订单号:" + pay_no)
        # result = get_order_result(pay_no, pay_results[0].nonce_str, pay_results[0].sign)
        account_id = pay_results[0].account_id
        pay_results[0].update(ispay=1, update_time=timezone.now)
        AccountDetail.objects.filter(is_delete=0).filter(account_id=account_id).update(ispay=1,
                                                                                       update_time=timezone.now)

        return HttpResponseRedirect('/subscription/detail?account_id=%s' % account_id)


class WechatViewSet(View):
    wechat_api = WechatLogin()


class AuthView(WechatViewSet):
    def get(self, request):
        url = self.wechat_api.get_code_url()
        print("redirect url is ", url)
        return redirect(url)


class GetInfoView(WechatViewSet):
    def get(self, request):
        if 'code' in request.GET:
            code = request.GET['code']
            token, openid = self.wechat_api.get_access_token(code)
            if token is None or openid is None:
                return HttpResponseServerError('get code error')
            user_info, error = self.wechat_api.get_user_info(token, openid)
            if error:
                return HttpResponseServerError('get access_token error')
            print(user_info)
            user_data = {
                'nickname': user_info['nickname'],
                'sex': user_info['sex'],
                'province': user_info['province'].encode('iso8859-1').decode('utf-8'),
                'city': user_info['city'].encode('iso8859-1').decode('utf-8'),
                'country': user_info['country'].encode('iso8859-1').decode('utf-8'),
                'avatar': user_info['headimgurl'],
                'openid': user_info['openid']
            }
            # return JsonResponse(user_data)
            users = User.objects.filter(is_delete=0).filter(open_id=user_data['openid'])
            if users.count() == 0:
                users = User.objects.create(nick_name=user_data['nickname'],
                                            img_url=user_data['avatar'],
                                            open_id=user_data['openid'])
                # create不需要users.save()
            accounts = Account.objects.filter(is_delete=0).filter(open_id=user_data['openid'])
            context = {'user': user_data['nickname'].encode('iso8859-1').decode('utf-8'),
                       'open_id': user_data['openid'],
                       'img_url': user_data['avatar'], 'account_list': accounts}
            response = render(request, '0home_list.html', context)
            response.set_cookie('openid', openid, expires=60 * 60 * 24 * 30)
            return response


class GetAccountListView(WechatViewSet):
    def get(self, request):
        if 'open_id' in request.GET:
            open_id = request.GET['open_id']
            users = User.objects.filter(is_delete=0).filter(open_id=open_id)
            user_name = users[0].nick_name.encode('iso8859-1').decode('utf-8')
            user_img_url = users[0].img_url
            accounts = Account.objects.filter(is_delete=0).filter(open_id=open_id)
            account_list = []
            for account in accounts:
                account_list.append(account.user_name)
            context = {'user': user_name,
                       'open_id': open_id,
                       'img_url': user_img_url}
            return render(request, '1account_list.html', context)


class GetAccountDetailView(WechatViewSet):
    def get(self, request):
        if 'account_id' in request.GET:
            account_id = request.GET['account_id']
            # open_id = request.GET['open_id']
            account = Account.objects.get(id=account_id)
            open_id = account.open_id
            users = User.objects.filter(is_delete=0).filter(open_id=open_id)
            account_details = AccountDetail.objects.filter(is_delete=0).filter(open_id=open_id).filter(
                account_id=account_id)
            user_name = users[0].nick_name.encode('iso8859-1').decode('utf-8')
            user_img_url = users[0].img_url
            user_account_name = account.user_name
            user_account_pwd = account.user_pwd
            user_account_status = user_status_dict.get(account.user_status)
            if account_details.count() == 0:
                context = {'user_name': user_name,
                           'open_id': open_id,
                           'account_id': account_id,
                           'user_account_name': user_account_name,
                           'user_account_pwd': user_account_pwd,
                           'user_account_status': user_account_status,
                           'user_img_url': user_img_url,
                           'blog_url': '',
                           'blog_pwd': '',
                           'photo_url': '',
                           'photo_pwd': '',
                           'params': get_jsapi_params(open_id)}
            else:
                blog_url = account_details[0].blog_url
                blog_pwd = account_details[0].blog_pwd
                photo_url = account_details[0].photo_url
                photo_pwd = account_details[0].photo_pwd
                is_pay = account_details[0].is_pay
                context = {'user_name': user_name,
                           'open_id': open_id,
                           'account_id': account_id,
                           'user_account_name': user_account_name,
                           'user_account_pwd': user_account_pwd,
                           'user_account_status': user_account_status,
                           'user_img_url': user_img_url,
                           'blog_url': blog_url,
                           'blog_pwd': blog_pwd if is_pay else "********",
                           'photo_url': photo_url,
                           'photo_pwd': photo_pwd if is_pay else "********",
                           'params': get_jsapi_params(open_id)}
            print(context)
            return render(request, '2account_detail.html', context)


class GetAccountPay(View):
    def get(self, request, *args, **kwargs):
        """
        用户点击一个路由或者扫码进入这个views.py中的函数，首先获取用户的openid,
        使用jsapi方式支付需要此参数
        :param self:
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        open_id = request.GET['open_id']
        account_id = request.GET['account_id']
        if not open_id:
            open_id = get_openid(request.GET.get('code'), request.GET.get('state', ''))
            if not open_id:
                return HttpResponse('获取用户openid失败')
        users = User.objects.filter(is_delete=0).filter(open_id=open_id)
        img_url = users[0].img_url
        params_dict = get_jsapi_params(open_id)
        AccountPay.objects.create(
            account_id=account_id,
            pay_no=params_dict.get('out_trade_no'),
            # prepay_no=params_dict.get('prepay_id'),
            # nonce_str=params_dict.get('nonce_str'),
            # sign=params_dict.get('sign')
        )
        response = render(request, '3account_pay.html',
                          context={'img_url': img_url, 'params': params_dict})
        response.set_cookie('openid', open_id, expires=60 * 60 * 24 * 30)
        return response


# django默认开启csrf防护，这里使用@csrf_exempt去掉防护
@csrf_exempt
def weixin_check(request):
    if request.method == 'GET':
        signature = request.GET.get('signature', None)
        timestamp = request.GET.get('timestamp', None)
        nonce = request.GET.get('nonce', None)
        echostr = request.GET.get('echostr', None)
        token = 'yiqian'
        hashlist = [token, timestamp, nonce]
        hashlist.sort()
        print('[token, timestamp, nonce]', hashlist)
        hashstr = ''.join(hashlist).encode('utf-8')
        print('hashstr before sha1', hashstr)
        hashstr = hashlib.sha1(hashstr).hexdigest()
        print('hashstr after sha1', hashstr)
        print('signature is ', signature)
        if hashstr == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse('error')
    else:
        return HttpResponse('...')
