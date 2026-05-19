from fastapi import FastAPI,Request,Form,status,Response,Depends,HTTPException,Cookie,responses,File,UploadFile
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import User
from Model import Notif
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
from Controller.login import check_token
from Controller.login import create_username_token
from typing import List
import uuid
import shutil
# from main import semaphore

# ایجاد یک router جدید
router = APIRouter()
template=Jinja2Templates(directory="templates")

# اطمینان از وجود دایرکتوری برای ذخیره عکس‌ها
NOTIF_IMG_DIR = "static/notif_img"
os.makedirs(NOTIF_IMG_DIR, exist_ok=True)

NOTIF_ATTACH_DIR = "static/notif_attach"
os.makedirs(NOTIF_ATTACH_DIR, exist_ok=True)

def save_file(UPLOAD_DIR:str,file:UploadFile)->str:
    # تولید اسم یونیک برای عکس
    ext = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    # ذخیره عکس
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return filename


async def fetch_url(client,url,request):
    semaphore=request.app.state.semaphore
    async with semaphore:
        response=await client.get(url,timeout=10)
        if response.status_code == status.HTTP_200_OK:
            h=response.json()
        else:
            h=[]
        return h



@router.get("/",response_class=HTMLResponse)
@router.get("/index",response_class=HTMLResponse)
async def index(request:Request,response: Response,page:str="1"):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        # return user_data
        user_data={}

    # # if user_data["type"] != "0":
    # #     return responses.RedirectResponse(url="/logout")
    try:
        ujtoken=create_username_token({"username":user_data["username"]})
        username_show=user_data["username"]
    except:
        ujtoken=create_username_token({"username":"public"})
        username_show="public"

    # ######
    page=int(page)
    urls = ['http://127.0.0.1:8001/index/moavenat/list' #لیست معاونت ها
    ,'http://127.0.0.1:8001/notif/count/important/True' #تعداد صفحات
    ,'http://127.0.0.1:8001/index/notif?show=True&page='+str(page)  #آگهی ها اصلی
    ,'http://127.0.0.1:8001/index/notif?show=True&important=True' # آگهی های مهم
    ,'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True'  #ثبت نام ها
    , 'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' #نظر سنجی ها
    ,'http://127.0.0.1:8001/index/tag' #تگ ها

    ] # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient(headers=headers) as client:
        tasks=[fetch_url(client,u,request)for u in urls]
        results =await asyncio.gather(*tasks)
    moavenat_list,page_count,main_notif_list,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list=results  

    try:
        page_count=int(page_count)+9    
        page_count=page_count//10
    except:
        page_count=1

    

    return template.TemplateResponse('index/index.html',{'request':request,"username":username_show,"page":page,"page_count":page_count,"user_data":user_data,"tag_list":tag_list,"sinup_show_list":sinup_show_list,"survay_show_list":survay_show_list,"moavenats":moavenat_list,"main_notif_list":main_notif_list,"main_notif_list_admin":main_notif_list_admin})

  
@router.get("/old",response_class=HTMLResponse)
@router.get("/index/old",response_class=HTMLResponse)
async def index(request:Request,response: Response,page:str="1"):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        # return user_data
        user_data={}

    # # if user_data["type"] != "0":
    # #     return responses.RedirectResponse(url="/logout")
    try:
        ujtoken=create_username_token({"username":user_data["username"]})
        username_show=user_data["username"]
    except:
        ujtoken=create_username_token({"username":"public"})
        username_show="public"

    # ######
    page=int(page)
    #لیست معاونت ها
    url = 'http://127.0.0.1:8001/index/moavenat/list' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            moavenat_list=response.json()
            # return str(moavenat_list)
        else:
            moavenat_list=[]

    #تعداد صفحات آگهی 
    url = 'http://127.0.0.1:8001/notif/count/important/True' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            count=response.json()
            # return str(count)
            count=int(count)+9
            page_count=count//10
        else:
            page_count=1
        # return (str(page_count))

    #آگهی های مهم کل اداره کل
    url = 'http://127.0.0.1:8001/index/notif?important=True&show=True&page='+str(page) # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            main_notif_list=response.json()
            # return str(moavenat_list)
        else:
            main_notif_list=[]

    #آگهی های مهم ادمین
    url = 'http://127.0.0.1:8001/index/notif?show=True&important=True' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            main_notif_list_admin=response.json()
            # return str(moavenat_list)
        else:
            moavenat_list=[]

    #ثبت نام ها
    url = 'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            sinup_show_list=response.json()
            # return str(sinup_show_list)
        else:
            sinup_show_list=[]
    
    #نظر سنجی ها
    url = 'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            survay_show_list=response.json()
            # return str(moavenat_list)
        else:
            survay_show_list=[]

        #تگ ها
    url = 'http://127.0.0.1:8001/index/tag' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            tag_list=response.json()
            # return str(tag_list)
        else:
            tag_list=[]

    return template.TemplateResponse('index/index.html',{'request':request,"username":username_show,"page":page,"page_count":page_count,"user_data":user_data,"tag_list":tag_list,"sinup_show_list":sinup_show_list,"survay_show_list":survay_show_list,"moavenats":moavenat_list,"main_notif_list":main_notif_list,"main_notif_list_admin":main_notif_list_admin})


@router.get("/notif/{moavenat}",response_class=HTMLResponse)
async def index_mo(request:Request,response: Response,moavenat:str,page:str="1"):
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        # return user_data
        user_data={}

    # # if user_data["type"] != "0":
    # #     return responses.RedirectResponse(url="/logout")
    try:
        ujtoken=create_username_token({"username":user_data["username"]})
        username_show=user_data["username"]
    except:
        ujtoken=create_username_token({"username":"public"})
        username_show="public"
    # ######


    page=int(page)
    urls = ['http://127.0.0.1:8001/index/moavenat/list' #لیست معاونت ها
    ,'http://127.0.0.1:8001/notif/count/moavenat/'+moavenat #تعداد صفحات
    ,'http://127.0.0.1:8001/index/notif?moavenat='+moavenat+'&page='+str(page) #آگهی ها اصلی
    ,'http://127.0.0.1:8001/index/notif?moavenat='+moavenat+"&important=True" # معاونت آگهی های مهم
    ,'http://127.0.0.1:8001/index/notif?show=True&important=True' # آگهی های مهم ادمین
    ,'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True'  #ثبت نام ها
    , 'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' #نظر سنجی ها
    ,'http://127.0.0.1:8001/index/tag' #تگ ها
    ] # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient(headers=headers) as client:
        tasks=[fetch_url(client,u,request)for u in urls]
        results =await asyncio.gather(*tasks)
    moavenat_list,page_count,main_notif_list,main_notif_list_important,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list=results  

    try:
        page_count=int(page_count)+9    
        page_count=page_count//10
    except:
        page_count=1 

    return template.TemplateResponse('index/index_mo.html',{'request':request,"moavenat":moavenat,"username":username_show,"page":page,"page_count":page_count,"moven":moavenat,"user_data":user_data,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"moavenats":moavenat_list,"main_notif_list":main_notif_list,"main_notif_list_admin":main_notif_list_admin,"main_notif_list_important":main_notif_list_important})

@router.get("/notif/old{moavenat}",response_class=HTMLResponse)
async def index_mo(request:Request,response: Response,moavenat:str,page:str="1"):
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        # return user_data
        user_data={}

    # # if user_data["type"] != "0":
    # #     return responses.RedirectResponse(url="/logout")
    try:
        ujtoken=create_username_token({"username":user_data["username"]})
        username_show=user_data["username"]
    except:
        ujtoken=create_username_token({"username":"public"})
        username_show="public"
    # ######
    
    #لیست معاونت ها
    url = 'http://127.0.0.1:8001/index/moavenat/list' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            moavenat_list=response.json()
            # return str(moavenat_list)
        else:
            moavenat_list=[]
    page=int(page)
    #تعداد صفحات آگهی 
    url = 'http://127.0.0.1:8001/notif/count/moavenat/'+moavenat # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            count=response.json()
            # return str(count)
            count=int(count)+9
            page_count=count//10
        else:
            page_count=1
        # return (str(count))

    #آگهی های   معاونت
    url = 'http://127.0.0.1:8001/index/notif?moavenat='+moavenat+'&page='+str(page) # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            main_notif_list=response.json()
            # return str(moavenat_list)
        else:
            main_notif_list=[]

    

    #آگهی های مهم  معاونت
    url = 'http://127.0.0.1:8001/index/notif?moavenat='+moavenat+"&important=True" # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            main_notif_list_important=response.json()
            # return str(moavenat_list)
        else:
            main_notif_list_important=[]

    #آگهی های مهم ادمین
    url = 'http://127.0.0.1:8001/index/notif?show=True&important=True' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            main_notif_list_admin=response.json()
            # return str(moavenat_list)
        else:
            main_notif_list_admin=[]


    #ثبت نام ها
    url = 'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    # return "ss"
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            sinup_show_list=response.json()
            # return str(sinup_show_list)
        else:
            sinup_show_list=[]
    
    #نظر سنجی ها
    url = 'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            survay_show_list=response.json()
            # return str(moavenat_list)
        else:
            survay_show_list=[]

            #تگ ها
    url = 'http://127.0.0.1:8001/index/tag' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            tag_list=response.json()
            # return str(tag_list)
        else:
            tag_list=[]

    return template.TemplateResponse('index/index_mo.html',{'request':request,"username":username_show,"page":page,"page_count":page_count,"moven":moavenat,"user_data":user_data,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"moavenats":moavenat_list,"main_notif_list":main_notif_list,"main_notif_list_admin":main_notif_list_admin,"main_notif_list_important":main_notif_list_important})


@router.get("/notif/single/{itemid}",response_class=HTMLResponse)
async def notif(request:Request,response: Response,itemid:str):

    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    # ujtoken=create_username_token({"username":"public"})
    ######



    urls = ['http://127.0.0.1:8001/index/moavenat/list' #لیست معاونت ها
    ,'http://127.0.0.1:8001/comment/'+itemid+'/notif/all/'+user_data["username"] #کل کامنت ها به جز کامنت شخص
    ,'http://127.0.0.1:8001/comment/'+itemid+'/notif/'+user_data["username"]+'/0' #کامنت های شخص زیر پست
    ,'http://127.0.0.1:8001/index/notif?show=True&important=True' # آگهی های مهم ادمین
    ,'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True'  #ثبت نام ها
    , 'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' #نظر سنجی ها
    ,'http://127.0.0.1:8001/index/tag' #تگ ها
    ,'http://127.0.0.1:8001/notif/detail/'+itemid #گرفتن اطلاعیه 
    ] # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient(headers=headers) as client:
        tasks=[fetch_url(client,u,request)for u in urls]
        results =await asyncio.gather(*tasks)
    moavenat_list,all_comment,user_comment,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list,notifs=results  

    try:
        notif = notifs[0]
    except:
        notif = None

    return template.TemplateResponse('index/notif_single.html',{'request':request,"user_data":user_data,"status":"ok","notif":notif,"moavenats":moavenat_list,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"main_notif_list_admin":main_notif_list_admin,"all_comment":all_comment,"user_comment":user_comment})



@router.get("/notif/single/{itemid}/old",response_class=HTMLResponse)
async def notif(request:Request,response: Response,itemid:str):

    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    # ujtoken=create_username_token({"username":"public"})
    ######
        #لیست معاونت ها
    url = 'http://127.0.0.1:8001/index/moavenat/list' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            moavenat_list=response.json()
            # return str(moavenat_list)
        else:
            moavenat_list=[]


    #کل کامنت ها به جز کامنت شخص
    url = 'http://127.0.0.1:8001/comment/'+itemid+'/notif/all/'+user_data["username"] # آدرس URL
    # return url
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            all_comment=response.json()
            # return str(all_comment)
        else:
            all_comment=[]


    #کامنت های شخص زیر پست
    url = 'http://127.0.0.1:8001/comment/'+itemid+'/notif/'+user_data["username"]+'/0' # آدرس URL
    # return url
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            user_comment=response.json()
            # return str(user_comment)
        else:
            user_comment=[]




        #لیست معاونت ها
    url = 'http://127.0.0.1:8001/index/moavenat/list' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            moavenat_list=response.json()
            # return str(moavenat_list)
        else:
            moavenat_list=[]

    #آگهی های مهم کل اداره کل
    url = 'http://127.0.0.1:8001/index/notif?important=True&show=True' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            main_notif_list=response.json()
            # return str(moavenat_list)
        else:
            moavenat_list=[]

    #آگهی های مهم ادمین
    url = 'http://127.0.0.1:8001/index/notif?show=True&important=True' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            main_notif_list_admin=response.json()
            # return str(moavenat_list)
        else:
            moavenat_list=[]

    #ثبت نام ها
    url = 'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            sinup_show_list=response.json()
            # return str(sinup_show_list)
        else:
            sinup_show_list=[]
    
    #نظر سنجی ها
    url = 'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            survay_show_list=response.json()
            # return str(moavenat_list)
        else:
            survay_show_list=[]

        #تگ ها
    url = 'http://127.0.0.1:8001/index/tag' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            tag_list=response.json()
            # return str(tag_list)
        else:
            tag_list=[]


    
    #گرفتن اطلاعیه قبلی
    url = 'http://127.0.0.1:8001/notif/detail/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            notifs=response.json()
            # return str(notifs)
            try:
                notif = notifs[0]
            except:
                notif = None
            return template.TemplateResponse('index/notif_single.html',{'request':request,"user_data":user_data,"status":"ok","notif":notif,"moavenats":moavenat_list,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"main_notif_list":main_notif_list,"main_notif_list_admin":main_notif_list_admin,"all_comment":all_comment,"user_comment":user_comment})
        else:
            return responses.RedirectResponse(url="/index")
