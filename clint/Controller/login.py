from fastapi import FastAPI,Request,Form,status,Response,Depends,HTTPException,Cookie,responses
import fastapi
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import User
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import requests
import json
import hashlib
import httpx
import asyncio
from datetime import datetime, timedelta
import jwt
from typing import Optional
from fastapi.responses import JSONResponse,HTMLResponse
from fastapi.security import HTTPBearer



# ایجاد یک router جدید
router = APIRouter()
template=Jinja2Templates(directory="templates")


# کلید مخفی برای امضای توکن
SECRET_KEY = "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# کلید مخفی برای ارسال نام کاربری در هدر درخواست ها
SECRET_KEY_USERNAME = "0041e6ad98c3ae252d"
ALGORITHM_USERNAME = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES_USERNAME = 5


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()  # داده‌هایی که می‌خواهید در توکن ذخیره شود
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=120)
    to_encode.update({"exp": expire})  # تاریخ انقضا را اضافه می‌کنیم
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # توکن را رمزنگاری می‌کنیم
    
    return encoded_jwt


def create_username_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()  # داده‌هایی که می‌خواهید در توکن ذخیره شود
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"exp": expire})  # تاریخ انقضا را اضافه می‌کنیم
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY_USERNAME, algorithm=ALGORITHM_USERNAME)  # توکن را رمزنگاری می‌کنیم
    
    return encoded_jwt

# def get_token(swtoken:str=Cookie(default=None)):
#     return swtoken

async def check_token(request:Request):
    # return "s"
    token = request.cookies.get("swtoken")  # گرفتن JWT از کوکی
    # print(token,"+-+-+-+-+-")
    # return token
    if not token:
        # return template.TemplateResponse('login/login.html',{'request':request})
        # print ("not token -------------------------")
        return RedirectResponse(url="/login")
    else:
        try:
            token_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except:
            # print ("expire-------------------------")
            # return template.TemplateResponse('login/login.html',{'request':request})
            return responses.RedirectResponse(url="/logout")
        
        # async req remove active session
        url = 'http://127.0.0.1:8001/check_active_session'  # آدرس URL
        headers = {
            'Content-Type': 'application/json',
            'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc'  # مثال: هدر احراز هویت
        }
        data = {"username":token_info["username"],"token":token}

        async with httpx.AsyncClient() as client:
            response_check_sesion = await client.post(url, headers=headers, json=data)
            # return str(response_check_sesion.content)
            if response_check_sesion.status_code==status.HTTP_200_OK:
                # print (str(token_info),"*****************")
                return token_info
            else:
                # return "False"
                # print ("tokenfasle --------------")
                return responses.RedirectResponse(url="/logout")
                

@router.get("/login",response_class=HTMLResponse)
async def login(request:Request):
    return template.TemplateResponse('login/login.html',{'request':request})


@router.post("/login",response_class=HTMLResponse)
async def login(request:Request,response: Response,user: User.User_login=Form("")):
    #async req
    url = 'http://127.0.0.1:8001/login'  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc'  # مثال: هدر احراز هویت
    }
    user.password=hashlib.sha1(user.password.encode()).hexdigest()
    data = user.__dict__
    # return str(data)
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        if response.status_code == status.HTTP_200_OK:
            result=response.json()
            # return str(user_d)
            user_d=result["user"]
            dict_info={"username":user_d["username"],"type":user_d["type_user"]}
            # return str(dict_info)
            token=create_access_token(dict_info)

            #async req insert active session
            url_insert_session = 'http://127.0.0.1:8001/insert_active_session'  # آدرس URL
            headers_insert_session = {
                'Content-Type': 'application/json',
                'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc'  # مثال: هدر احراز هویت
            }
            data_insert_session = {"username":user_d["username"],"token":token}

            async with httpx.AsyncClient() as client:
                response_add_sesion = await client.post(url_insert_session, headers=headers_insert_session, json=data_insert_session)
                # result=response_add_sesion.json()
                # return str(response_add_sesion.content)
                if response_add_sesion.status_code==status.HTTP_200_OK:
                    # return "ok"
                     # تنظیم کوکی در شیء Response
                    if user_d["type_user"] =="100":
                        response = template.TemplateResponse('login/rabet.html', {'request': request,"rabet":"/index"})
                    else:
                        response = template.TemplateResponse('login/rabet.html', {'request': request,"rabet":"notif/index"})
                    
                    response.set_cookie(key="swtoken", value=token, httponly=True, secure=False, samesite="Lax")
                    
                    # بازگرداندن پاسخ به همراه کوکی
                    return response
                else:
                    return template.TemplateResponse('/login/login.html',{'request':request,"status":"false"})        
        elif response.status_code==status.HTTP_400_BAD_REQUEST :
            return template.TemplateResponse('login/login.html',{'request':request,"status":"badreq"})
        elif response.status_code==status.HTTP_404_NOT_FOUND :
            return template.TemplateResponse('login/login.html',{'request':request,"status":"false"})



LDAP_SERVER = "ldap://"  # ← آدرس IP دامین کنترلر
DOMAIN = ""                      # ← نام NetBIOS دامنه (نه test.local، فقط TEST)


@router.get("/login/public",response_class=HTMLResponse)
async def login(request:Request):
    return template.TemplateResponse('login/login_public.html',{'request':request})


@router.post("/login/public",response_class=HTMLResponse)
async def login(request:Request,response: Response,user_f: User.User_login=Form("")):
    username=user_f.username
    password=user_f.password
    # return (str(username))
    user = f"{DOMAIN}\\{username}"
    # return (str(user))

    user_f.password=hashlib.sha1(password.encode()).hexdigest()
    data = user_f.__dict__
    try:
        token = win32security.LogonUser(
        username,
        DOMAIN,
        password,
        win32security.LOGON32_LOGON_NETWORK,
        win32security.LOGON32_PROVIDER_DEFAULT
        )
        
        dict_info={"username":username,"type":"100"}
        token=create_access_token(dict_info)

        #async req insert active session
        url_insert_session = 'http://127.0.0.1:8001/insert_active_session'  # آدرس URL
        headers_insert_session = {
            'Content-Type': 'application/json',
            'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc'  # مثال: هدر احراز هویت
        }
        data_insert_session = {"username":user_f.username,"token":token}

        async with httpx.AsyncClient() as client:
            response_add_sesion = await client.post(url_insert_session, headers=headers_insert_session, json=data_insert_session)
            # result=response_add_sesion.json()
            # return str(response_add_sesion.content)
            if response_add_sesion.status_code==status.HTTP_200_OK:
                # return "ok"
                    # تنظیم کوکی در شیء Response
                response = template.TemplateResponse('rabet.html', {'request': request,"rabet":"index/index.html"})
                response.set_cookie(key="swtoken", value=token, httponly=True, secure=False, samesite="Lax")
                
                # بازگرداندن پاسخ به همراه کوکی
                return response
            else:
                return template.TemplateResponse('/login/login_public.html',{'request':request,"status":"badreq"})   
    except Exception as e:
        return template.TemplateResponse('login/login_public.html',{'request':request,"status":"false"})
    
    




@router.get("/logout",response_class=HTMLResponse)
async def logout(request:Request):
    token = request.cookies.get("swtoken")  # گرفتن JWT از کوکی
    # return token
    if not token:
        # return template.TemplateResponse('login/login.html',{'request':request})
        return responses.RedirectResponse(url="/login")
    else:
        token_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],options={"verify_exp":False})
        
        # async req remove active session
        url = 'http://127.0.0.1:8001/remove_active_session'  # آدرس URL
        headers = {
            'Content-Type': 'application/json',
            'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc'  # مثال: هدر احراز هویت
        }
        data = {"username":token_info["username"],"token":token}

        async with httpx.AsyncClient() as client:
            response_remove_sesion = await client.post(url, headers=headers, json=data)
            if response_remove_sesion.status_code==status.HTTP_200_OK:

                # حذف کوکی
                # response = template.TemplateResponse('login/login.html', {'request': request})
                response = responses.RedirectResponse(url="/login")
                response.delete_cookie("swtoken")
                return response
            else:
                return token
            
@router.get("/test")
async def test(request:Request):
    return "s"
    st=check_token(request)
    return(st)



            




    




