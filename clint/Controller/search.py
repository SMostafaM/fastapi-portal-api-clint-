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



@router.api_route("/search/notif/main",methods=["POST","GET"],response_class=HTMLResponse)
async def index_mo(request:Request,response: Response,page:str="1",data:str=Form("defult"),data_save:str="defult"):
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
        # user_data={}

    # # if user_data["type"] != "0":
    # #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    # ######
    if request.method =="GET":
        data=data_save

    urls = ['http://127.0.0.1:8001/search/main?type_req=notif&data='+data+'&page='+str(page) #جستجو
    ,'http://127.0.0.1:8001/search/count/main?type_req=notif&data='+data #تعداد محصولات جستجو 
    ,'http://127.0.0.1:8001/index/moavenat/list' #لیست معاونت ها
    ,'http://127.0.0.1:8001/index/notif?show=True&important=True' # آگهی های مهم ادمین
    ,'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True'  #ثبت نام ها
    ,'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' #نظر سنجی ها
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
    main_notif_list,page_count,moavenat_list,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list=results  

    try:
        page_count=int(page_count)+9    
        page_count=page_count//10
    except:
        page_count=1

    return template.TemplateResponse('search/main.html',{'request':request,"data":data,"page":page,"page_count":page_count,"user_data":user_data,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"moavenats":moavenat_list,"main_notif_list":main_notif_list,"main_notif_list_admin":main_notif_list_admin})





@router.api_route("/search/notif",methods=["POST","GET"],response_class=HTMLResponse)
async def index_mo(request:Request,response: Response,page:str="1",data:str=Form("defult"),data_save:str="defult"):
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
        # user_data={}

    # # if user_data["type"] != "0":
    # #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    # ######
    if request.method =="GET":
        data=data_save

    urls = ['http://127.0.0.1:8001/search?type_req=notif&data='+data+'&page='+str(page) #جستجو
    ,'http://127.0.0.1:8001/search/count?type_req=notif&data='+data #تعداد محصولات جستجو 
    ,'http://127.0.0.1:8001/index/moavenat/list' #لیست معاونت ها
    ,'http://127.0.0.1:8001/index/notif?show=True&important=True' # آگهی های مهم ادمین
    ,'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True'  #ثبت نام ها
    ,'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' #نظر سنجی ها
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
    main_notif_list,page_count,moavenat_list,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list=results  

    try:
        page_count=int(page_count)+9    
        page_count=page_count//10
    except:
        page_count=1

    return template.TemplateResponse('search/notif.html',{'request':request,"data":data,"page":page,"page_count":page_count,"user_data":user_data,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"moavenats":moavenat_list,"main_notif_list":main_notif_list,"main_notif_list_admin":main_notif_list_admin})



@router.api_route("/search/post",methods=["POST","GET"],response_class=HTMLResponse)
async def post(request:Request,response: Response,data:str=Form("defult"),data_save:str="defult",page:int=1):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    # ujtoken=create_username_token({"username":"public"})
    ######
    if request.method =="GET":
        data=data_save

    urls = ['http://127.0.0.1:8001/search?type_req=post&data='+data+'&page='+str(page)#جستجو
    ,'http://127.0.0.1:8001/search/count?type_req=post&data='+data #تعداد محصولات جستجو 
    ,'http://127.0.0.1:8001/index/moavenat/list' #لیست معاونت ها
    ,'http://127.0.0.1:8001/index/notif?show=True&important=True' # آگهی های مهم ادمین
    ,'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True'  #ثبت نام ها
    , 'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' #نظر سنجی ها
    ,'http://127.0.0.1:8001/index/tag' #تگ ها
    ,'http://127.0.0.1:8001/post/tag/index'  #تگ کامل    
    ] # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient(headers=headers) as client:
        tasks=[fetch_url(client,u,request)for u in urls]
        results =await asyncio.gather(*tasks)
    main_post_list,page_count,moavenat_list,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list,tags=results  

    try:
        page_count=int(page_count)+9    
        page_count=page_count//10
    except:
        page_count=1
   

    return template.TemplateResponse('search/post.html',{'request':request,"data":data,"tags":tags,"page":int(page),"user_data":user_data,"main_post_list":main_post_list,"data":data,"page":page,"page_count":page_count,"tag_list":tag_list,"sinup_show_list":sinup_show_list,"survay_show_list":survay_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})

@router.api_route("/search/form/archive",methods=["POST","GET"],response_class=HTMLResponse)
async def post(request:Request,response: Response,data:str=Form("defult"),data_save:str="defult",page:int=1):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    # ujtoken=create_username_token({"username":"public"})
    ######
    if request.method =="GET":
        data=data_save
    # return data
    urls = ['http://127.0.0.1:8001/search?type_req=form_archive&data='+data+'&page='+str(page)#جستجو
    ,'http://127.0.0.1:8001/search/count?type_req=form_archive&data='+data #تعداد محصولات جستجو 
    ,'http://127.0.0.1:8001/index/moavenat/list' #لیست معاونت ها
    ,'http://127.0.0.1:8001/index/notif?show=True&important=True' # آگهی های مهم ادمین
    ,'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True'  #ثبت نام ها
    , 'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' #نظر سنجی ها
    ,'http://127.0.0.1:8001/index/tag' #تگ ها
    ,'http://127.0.0.1:8001/form/group/index'  #گرفتن آکهی 
    ] # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient(headers=headers) as client:
        tasks=[fetch_url(client,u,request)for u in urls]
        results =await asyncio.gather(*tasks)
    main_form_list,page_count,moavenat_list,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list,groups=results  

    try:
        page_count=int(page_count)+9    
        page_count=page_count//10
    except:
        page_count=1
   
#    return str(main_form_list)

    return template.TemplateResponse('search/form_archive.html',{'request':request,"groups":groups,"data":data,"page":int(page),"user_data":user_data,"main_form_list":main_form_list,"data":data,"page":page,"page_count":page_count,"tag_list":tag_list,"sinup_show_list":sinup_show_list,"survay_show_list":survay_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})
