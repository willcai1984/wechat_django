# -*- coding: utf-8 -*-

import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


# django默认开启csrf防护，这里使用@csrf_exempt去掉防护
@csrf_exempt
def weixin_check(request):
    if request.method == 'GET':
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')
        token = 'leartd'

        hashlist = [token, timestamp, nonce]
        hashlist.sort()
        print('[token, timestamp, nonce]', hashlist)
        hashstr = ''.join([s for s in hashlist]).encode('utf-8')
        print('hashstr before sha1', hashstr)
        hashstr = hashlib.sha1(hashstr).hexdigest()
        print('hashstr sha1', hashstr)
        if hashstr == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse('error')
    else:
        return HttpResponse('...')
