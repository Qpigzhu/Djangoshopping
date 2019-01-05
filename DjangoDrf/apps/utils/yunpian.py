# _*_ encoding:utf-8 _*_
__author__ = 'pig'
__data__ = '2018\12\5 0005 19:20$'

import requests
import json


class YunPian(object):

    def __init__(self,api_key):
        self.api_key = api_key
        self.single_send_url = "https://sms.yunpian.com/v2/sms/single_send.json"

    def send_sms(self,code,mobile):
        parmas = {
            "apikey":self.api_key,
            "mobile":mobile,
            "text":"【小猪超市】您的手机验证码{}，非本人操作，请忽略".format(code)

        }
        response = requests.post(self.single_send_url,data=parmas)
        re_dict = json.loads(response.text)

        return re_dict


if __name__ == '__main__':
    yun_pian = YunPian("c3f3f6e838aebdcd4cbbf02575104989")
    yun_pian.send_sms("2018","15625873905")