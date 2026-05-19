from fastapi import FastAPI,Request,Form,status,Response,Depends,HTTPException,Cookie,responses,File,UploadFile
from fastapi.responses import RedirectResponse
import fastapi
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
from Controller.login import check_token
from Controller.login import create_username_token
from Controller.index import index as main_index
import uuid
import shutil
from typing import Optional
# from main import semaphore


# ایجاد یک router جدید
router = APIRouter()
template=Jinja2Templates(directory="templates")

# اطمینان از وجود دایرکتوری برای ذخیره عکس‌ها
USER_IMG_DIR = "static/user_img"
os.makedirs(USER_IMG_DIR, exist_ok=True)


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

@router.get("/user_s/edite/self/{status_show}",response_class=HTMLResponse)
@router.get("/user_s/edite/self",response_class=HTMLResponse)
async def edite_s(request:Request,response: Response,status_show:str="nothing"):
    #check cookei
    # return ("ss")
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    
    urls = ['http://127.0.0.1:8001/user/detail/username/'+str(user_data["username"])  #گرفتن اطلاعات کامل کاربر
    ,'http://127.0.0.1:8001/index/moavenat/list' #لیست معاونت ها
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
    user,moavenat_list,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list=results  

    return template.TemplateResponse('user_s/edite_self.html',{'request':request,"user":user,"user_data":user_data,"status":status_show,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})
    
@router.get("/user_s/edite/self/{status_show}/old",response_class=HTMLResponse)
@router.get("/user_s/edite/self/old",response_class=HTMLResponse)
async def edite_s(request:Request,response: Response,status_show:str="nothing"):
    #check cookei
    # return ("ss")
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    # return (ujtoken)
    #گرفتن اطلاعات کامل کاربر
    url = 'http://127.0.0.1:8001/user/detail/username/'+str(user_data["username"])  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            user=response.json()
        else:
            user={}
        # return (str(user))

       

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

    

    

    # #آگهی های مهم  معاونت
    # url = 'http://127.0.0.1:8001/index/notif?moavenat='+moavenat+"&important=True" # آدرس URL
    # headers = {
    #     'Content-Type': 'application/json',
    #     'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
    #     "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    # }
    # async with httpx.AsyncClient() as client:
    #     response =await client.get(url, headers=headers)
    #     if response.status_code == status.HTTP_200_OK:
    #         main_notif_list_important=response.json()
    #         # return str(moavenat_list)
    #     else:
    #         main_notif_list_important=[]

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

    return template.TemplateResponse('user_s/edite_self.html',{'request':request,"user":user,"user_data":user_data,"status":status_show,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})
    




@router.post("/user_s/edite/self",response_class=HTMLResponse)
async def edite_s(request:Request,response: Response,id:str=Form(...),
username:str=Form(...),
name:str=Form(...),
password:str=Form(...),
type_user:str=Form(...),
img_upload: UploadFile = File(None)):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
   
    #ادیت کاربر
    # return (id)
    user=User.User_plus_complte(id=id,username=username,name=name,password=password,type_user=type_user,img="defult_user.jpg")
    if password != "":
        user.password=hashlib.sha1(user.password.encode()).hexdigest()
    data=user.dict()
    # return str(data)
    
    if img_upload and img_upload.filename !="":
        img_name=save_file(USER_IMG_DIR,img_upload)
    else:
        img_name="not_new_img"
    # return (img_name)
    data["img"]=img_name

    if password!= None and password!="":
        user.password=hashlib.sha1(user.password.encode()).hexdigest()

    # data=user.dict()
    # return str(data)
    url = 'http://127.0.0.1:8001/user/edite'  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }
    

    async with httpx.AsyncClient() as client:
        for attemp in range(1,3):
            try:
                response = await client.post(url, headers=headers, json=data,timeout=10)
                # return (str(response.status_code))
                if response.status_code == status.HTTP_200_OK:
                    # print("++++++++++++++ redirect ++++++++++++++")
                    # return responses.RedirectResponse(url="index")
                    # return await index_user(request,response)
                    status_edite="ok"

                elif  response.status_code == status.HTTP_404_NOT_FOUND:
                    # return template.TemplateResponse('/user/edite.html',{'request':request,"status":"Duplicate","user":user,"user_data":user_data})
                    # return responses.RedirectResponse(url="/user/edite/"+user.id+"/"+"Duplicate")
                    status_edite="Duplicate"
                else:
                    # return responses.RedirectResponse(url="/user/edite/"+data["id"]+"/"+"fasle",status_code=303)
                    status_edite="fasle"
            except Exception as e:
                if attemp < 3 :
                    await asyncio.sleep(1)
                else:
                   return {"error :", e}


    
    urls = ['http://127.0.0.1:8001/user/detail/username/'+str(user_data["username"])  #گرفتن اطلاعات کامل کاربر
    ,'http://127.0.0.1:8001/index/moavenat/list' #لیست معاونت ها
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
    user,moavenat_list,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list=results  


    return template.TemplateResponse('user_s/edite_self.html',{'request':request,"user":user,"user_data":user_data,"status":status_edite,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})


@router.post("/user_s/edite/self/old",response_class=HTMLResponse)
async def edite_s(request:Request,response: Response,id:str=Form(...),
username:str=Form(...),
name:str=Form(...),
password:str=Form(...),
type_user:str=Form(...),
img_upload: UploadFile = File(None)):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
   
    #ادیت کاربر
    # return (id)
    user=User.User_plus_complte(id=id,username=username,name=name,password=password,type_user=type_user,img="defult_user.jpg")
    if password != "":
        user.password=hashlib.sha1(user.password.encode()).hexdigest()
    data=user.dict()
    # return str(data)
    
    if img_upload and img_upload.filename !="":
        img_name=save_file(USER_IMG_DIR,img_upload)
    else:
        img_name="not_new_img"
    # return (img_name)
    data["img"]=img_name

    if password!= None and password!="":
        user.password=hashlib.sha1(user.password.encode()).hexdigest()

    # data=user.dict()
    # return str(data)
    url = 'http://127.0.0.1:8001/user/edite'  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }
    

    async with httpx.AsyncClient() as client:
        for attemp in range(1,3):
            try:
                response = await client.post(url, headers=headers, json=data,timeout=10)
                # return (str(response.status_code))
                if response.status_code == status.HTTP_200_OK:
                    # print("++++++++++++++ redirect ++++++++++++++")
                    # return responses.RedirectResponse(url="index")
                    # return await index_user(request,response)
                    status_edite="ok"

                elif  response.status_code == status.HTTP_404_NOT_FOUND:
                    # return template.TemplateResponse('/user/edite.html',{'request':request,"status":"Duplicate","user":user,"user_data":user_data})
                    # return responses.RedirectResponse(url="/user/edite/"+user.id+"/"+"Duplicate")
                    status_edite="Duplicate"
                else:
                    # return responses.RedirectResponse(url="/user/edite/"+data["id"]+"/"+"fasle",status_code=303)
                    status_edite="fasle"
            except Exception as e:
                if attemp < 3 :
                    await asyncio.sleep(1)
                else:
                   return {"error :", e}


    #گرفتن اطلاعات کامل کاربر
    url = 'http://127.0.0.1:8001/user/detail/username/'+str(user_data["username"])  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            user=response.json()
            # return template.TemplateResponse('user/edite_self.html',{'request':request,"user":user,"status":status_show,"user_data":user_data})
        else:
            # return responses.RedirectResponse(url="/index/user")
            user={}
        # return (str(user))
        

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

    

    

    # #آگهی های مهم  معاونت
    # url = 'http://127.0.0.1:8001/index/notif?moavenat='+moavenat+"&important=True" # آدرس URL
    # headers = {
    #     'Content-Type': 'application/json',
    #     'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
    #     "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    # }
    # async with httpx.AsyncClient() as client:
    #     response =await client.get(url, headers=headers)
    #     if response.status_code == status.HTTP_200_OK:
    #         main_notif_list_important=response.json()
    #         # return str(moavenat_list)
    #     else:
    #         main_notif_list_important=[]

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
    
    return template.TemplateResponse('user_s/edite_self.html',{'request':request,"user":user,"user_data":user_data,"status":status_edite,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})
