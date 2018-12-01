# -*- coding: utf-8 -*-
import hashlib

from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .models import Accout
from .models import User
from .models import AccountDetail
from .util import WechatLogin, check_account_renren


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


def add_account(request):
    if request.method == 'POST':
        user_name = request.POST['user_name']
        user_pwd = request.POST['user_pwd']
        open_id = request.POST['user_id']
        is_pass = check_account_renren(user_name, user_pwd)
        users = User.objects.filter(is_delete=0).filter(open_id=open_id)
        accounts = Accout.objects.filter(is_delete=0).filter(open_id=open_id)
        context = {'user': users[0].nick_name.encode('iso8859-1').decode('utf-8'),
                   'open_id': open_id,
                   'img_url': users[0].img_url,
                   'account_list': accounts}
        if is_pass:
            if Accout.objects.filter(is_delete=0).filter(open_id=open_id).filter(user_name=user_name).count() == 0:
                Accout.objects.create(
                    open_id=open_id,
                    user_name=user_name,
                    user_pwd=user_pwd
                )
            accounts = Accout.objects.filter(is_delete=0).filter(open_id=open_id)
            context = {'user': users[0].nick_name.encode('iso8859-1').decode('utf-8'),
                       'open_id': open_id,
                       'img_url': users[0].img_url,
                       'account_list': accounts}
            return render(request, '0home_list.html', context)
        else:
            return render(request, '0home_list.html', context)


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
            accounts = Accout.objects.filter(is_delete=0).filter(open_id=user_data['openid'])

            context = {'user': user_data['nickname'].encode('iso8859-1').decode('utf-8'),
                       'open_id': user_data['openid'],
                       'img_url': user_data['avatar'], 'account_list': accounts}
            return render(request, '0home_list.html', context)


class AccountListView(WechatViewSet):
    def get(self, request):
        if 'open_id' in request.GET:
            open_id = request.GET['open_id']
            users = User.objects.filter(is_delete=0).filter(open_id=open_id)
            user_name = users[0].nick_name.encode('iso8859-1').decode('utf-8')
            user_img_url = users[0].img_url
            accounts = Accout.objects.filter(is_delete=0).filter(open_id=open_id)
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
            open_id = request.GET['open_id']
            users = User.objects.filter(is_delete=0).filter(open_id=open_id)
            account_details = AccountDetail.objects.filter(is_delete=0).filter(open_id=open_id).filter(
                account_id=account_id)
            user_name = users[0].nick_name.encode('iso8859-1').decode('utf-8')
            user_img_url = users[0].img_url
            if account_details.count() == 0:
                print('无记录')
            else:
                blog_url = account_details[0].blog_url
                blog_pwd = account_details[0].blog_pwd
                photo_url = account_details[0].photo_url
                photo_pwd = account_details[0].photo_pwd
            for account in accounts:
                account_list.append(account.user_name)
            context = {'user': user_name,
                       'open_id': open_id,
                       'img_url': user_img_url}
            return render(request, '1account_list.html', context)
