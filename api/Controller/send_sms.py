import requests
from fastapi import APIRouter


router = APIRouter()

BaseAddress = "http://www.payamak.vip/api/v1/RestWebApi/"
userName='t.09396715121'
password='fql*877'




def  rest_send_sms(code,number):
    url=BaseAddress+'SendBatchSms'
    data={'userName': userName ,
          'password': password ,
          'fromNumber':'500025799991',
          'toNumbers':number,
          'messageContent':'سلام کد مورد ارسالی را برای احراز هویت وارد کنید.   verificate_code:'+str(code),
          'isFlash':False,
          'sendDelay':0
          }
    response = requests.post(url,json=data,headers={"Content-Type": "application/json"})
#     print(response.text)