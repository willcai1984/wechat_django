# -*- coding: utf-8 -*-

import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


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
