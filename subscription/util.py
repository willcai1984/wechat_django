# -*- coding: utf-8 -*-
# ----------------------------------------------
# @Time    : 18-3-21 下午1:36
# @Author  : YYJ
# @File    : WechatAPI.py
# @CopyRight: ZDWL
# ----------------------------------------------
import hashlib
import random
import time
import requests
from urllib import parse
from xml.etree.ElementTree import fromstring
from bs4 import BeautifulSoup
from . import utilconfig


class WechatAPI(object):
    def __init__(self):
        self.config = utilconfig
        self._access_token = None
        self._openid = None

    @staticmethod
    def process_response_login(rsp):
        """解析微信登录返回的json数据，返回相对应的dict, 错误信息"""
        if 200 != rsp.status_code:
            return None, {'code': rsp.status_code, 'msg': 'http error'}
        try:
            content = rsp.json()

        except Exception as e:
            return None, {'code': 9999, 'msg': e}
        if 'errcode' in content and content['errcode'] != 0:
            return None, {'code': content['errcode'], 'msg': content['errmsg']}

        return content, None

    def process_response_pay(self, rsp):
        """解析微信支付下单返回的json数据，返回相对应的dict, 错误信息"""
        rsp = self.xml_to_array(rsp)
        if 'SUCCESS' != rsp['return_code']:
            return None, {'code': '9999', 'msg': rsp['return_msg']}
        if 'prepay_id' in rsp:
            return {'prepay_id': rsp['prepay_id']}, None

        return rsp, None

    @staticmethod
    def create_time_stamp():
        """产生时间戳"""
        now = time.time()
        return int(now)

    @staticmethod
    def create_nonce_str(length=32):
        """产生随机字符串，不长于32位"""
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        strs = []
        for x in range(length):
            strs.append(chars[random.randrange(0, len(chars))])
        return "".join(strs)

    @staticmethod
    def xml_to_array(xml):
        """将xml转为array"""
        array_data = {}
        root = fromstring(xml)
        for child in root:
            value = child.text
            array_data[child.tag] = value
        return array_data

    def array_to_xml(self, dic, sign_name=None):
        """array转xml"""
        if sign_name is not None:
            dic[sign_name] = self.get_sign()
        xml = ["<xml>"]
        for k in dic.keys():
            xml.append("<{0}>{1}</{0}>".format(k, dic[k]))
        xml.append("</xml>")
        return "".join(xml)


class WechatLogin(WechatAPI):
    def get_code_url(self):
        """微信内置浏览器获取网页授权code的url"""
        url = self.config.defaults.get('wechat_browser_code') + (
                '?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=%s#wechat_redirect' %
                (self.config.APPID, parse.quote(self.config.REDIRECT_URI),
                 self.config.SCOPE, self.config.STATE if self.config.STATE else ''))
        return url

    def get_code_url_pc(self):
        """pc浏览器获取网页授权code的url"""
        url = self.config.defaults.get('pc_QR_code') + (
                '?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=%s#wechat_redirect' %
                (self.config.APPID, parse.quote(self.config.REDIRECT_URI), self.config.PC_LOGIN_SCOPE,
                 self.config.STATE if self.config.STATE else ''))
        return url

    def get_access_token(self, code):
        """获取access_token"""
        params = {
            'appid': self.config.APPID,
            'secret': self.config.APPSECRET,
            'code': code,
            'grant_type': 'authorization_code'
        }
        token, err = self.process_response_login(requests
                                                 .get(self.config.defaults.get('wechat_browser_access_token'),
                                                      params=params))
        if not err:
            self._access_token = token['access_token']
            self._openid = token['openid']
        return self._access_token, self._openid

    def get_user_info(self, access_token, openid):
        """获取用户信息"""
        params = {
            'access_token': access_token,
            'openid': openid,
            'lang': self.config.LANG
        }
        return self.process_response_login(requests
                                           .get(self.config.defaults.get('wechat_browser_user_info'), params=params))


class WechatPayAPI(WechatAPI):
    def __init__(self, package, sign_type=None):
        super().__init__()
        self.appId = self.config.APPID
        self.timeStamp = self.create_time_stamp()
        self.nonceStr = self.create_nonce_str()
        self.package = package
        self.signType = sign_type
        self.dic = {"appId": self.appId, "timeStamp": "{0}".format(self.create_time_stamp()),
                    "nonceStr": self.create_nonce_str(), "package": "prepay_id={0}".format(self.package)}
        if sign_type is not None:
            self.dic["signType"] = sign_type
        else:
            self.dic["signType"] = "MD5"

    def get_dic(self):
        self.dic['paySign'] = self.get_sign()
        return self.dic


def check_account_renren(user_name, user_pwd):
    headers = {
        'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    url_3g = "http://3g.renren.com/login.do?autoLogin=true&&fx=0"
    data = {'email': user_name,
            'password': user_pwd}
    req = requests.Session()
    login_res = req.post(url_3g, data=data, headers=headers)
    login_bs = BeautifulSoup(login_res.text, "html.parser")
    if login_bs.title.string.strip() == '手机人人网':
        # 成功登陆
        print('账号密码验证成功')
        return True
    elif login_bs.title.string.strip() == '手机人人网 - 因为真实，所以精彩':
        print('账号密码验证失败')
        return False
    else:
        print('其他原因')
        return False
