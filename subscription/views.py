# -*- coding: utf-8 -*-
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from .util import WechatLogin
from django.http import JsonResponse


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


class WechatViewSet(View):
    wechat_api = WechatLogin()


class AuthView(WechatViewSet):
    def get(self, request):
        url = self.wechat_api.get_code_url()
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
            user_data = {
                'nickname': user_info['nickname'],
                'sex': user_info['sex'],
                'province': user_info['province'].encode('iso8859-1').decode('utf-8'),
                'city': user_info['city'].encode('iso8859-1').decode('utf-8'),
                'country': user_info['country'].encode('iso8859-1').decode('utf-8'),
                'avatar': user_info['headimgurl'],
                'openid': user_info['openid']
            }
            return JsonResponse(user_data)

            # user = BeautyUsers.objects.filter(is_effective=True).filter(wechat=user_data['openid'])
            # if user.count() == 0:
            #     user = BeautyUsers.objects.create(username=user_data['nickname'],
            #                                       wechat_avatar=user_data['avatar'],
            #                                       wechat=user_data['openid'],
            #                                       password='')
            #     login(request, user)
            # else:
            #     login(request, user.first())
            # # 授权登录成功，进入主页
            # return home(request)
