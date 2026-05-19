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



@router.get("/user/index",response_class=HTMLResponse)
@router.get("/index/user",response_class=HTMLResponse)
async def index_user(request:Request,response: Response):

    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    if user_data["type"] != "0":
        return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    
    url = 'http://127.0.0.1:8001/user/index'  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            users=response.json()
            # return str(users)
            return template.TemplateResponse('user/index.html',{'request':request,"status":"ok","users":users,"user_data":user_data})
        else:
            return template.TemplateResponse('login/login.html',{'request':request,"status":"duplicate"})

@router.get("/user/create",response_class=HTMLResponse)
async def create(request:Request):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    if user_data["type"] != "0":
        return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######

    return template.TemplateResponse('user/create.html',{'request':request,"user_data":user_data})


@router.post("/user/create",response_class=HTMLResponse)
async def create(request:Request,response: Response,
username:str=Form(...),
name:str=Form(...),
password:str=Form(...),
type_user:str=Form(...),
img_upload: UploadFile = File(None)):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    if user_data["type"] != "0":
        return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    user=User.User_plus(username=username,name=name,password=password,type_user=type_user,img="defult_user.jpg")
    user.password=hashlib.sha1(user.password.encode()).hexdigest()
    data=user.dict()
    # return str(data)
    
    if img_upload and img_upload.filename !="":
        img_name=save_file(USER_IMG_DIR,img_upload)
    else:
        img_name="defult_user.jpg"
    data["img"]=img_name
    # return str(data)
    
    url = 'http://127.0.0.1:8001/user/create'  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }
    

    async with httpx.AsyncClient() as client:
        for attemp in range(1,3):
            try:
                response = await client.post(url, headers=headers, json=data,timeout=10)
                # return str(response.content)
                if response.status_code == status.HTTP_200_OK:
                    return template.TemplateResponse('/user/create.html',{'request':request,"status":"ok","user_data":user_data})
                elif  response.status_code == status.HTTP_404_NOT_FOUND:
                    return template.TemplateResponse('/user/create.html',{'request':request,"status":"Duplicate","user_data":user_data})
                else:
                    return template.TemplateResponse('/user/create.html',{'request':request,"status":"flase","user_data":user_data})
            except Exception as e:
                if attemp < 3 :
                    await asyncio.sleep(1)
                else:
                    return {"error :", e}



@router.get("/user/edite/{itemid}/{status_show}",response_class=HTMLResponse)
@router.get("/user/edite/{itemid}",response_class=HTMLResponse)
async def edite(itemid:str,request:Request,status_show:str="nothing"):
   #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    if user_data["type"] != "0":
        return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    url = 'http://127.0.0.1:8001/user/detail/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            users=response.json()
            # return str(users[0])
            try:
                return template.TemplateResponse('/user/edite.html',{'request':request,"user":users[0],"status":status_show,"user_data":user_data})
            except:
                return responses.RedirectResponse(url="/index/user")
            
        else:
            return responses.RedirectResponse(url="/index/user")






@router.post("/user/edite",response_class=HTMLResponse)
async def edite(request:Request,response: Response,
id:str=Form(...),
username:str=Form(...),
name:str=Form(...),
password:str=Form(...),
type_user:str=Form(...),
img_upload: UploadFile = File(None)):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    if user_data["type"] != "0":
        return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    # return (id)
    user=User.User_plus_complte(id=id,username=username,name=name,password=password,type_user=type_user,img="defult_user.jpg")
    if password != "":
        user.password=hashlib.sha1(user.password.encode()).hexdigest()
    data=user.dict()
    # return str(data)
    
    if img_upload and img_upload.filename !="":
        img_name=save_file(USER_IMG_DIR,img_upload)
    else:
        img_name="defult_user.jpg"
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
                if response.status_code == status.HTTP_200_OK:
                    # print("++++++++++++++ redirect ++++++++++++++")
                    # return responses.RedirectResponse(url="index")
                    return await index_user(request,response)

                elif  response.status_code == status.HTTP_404_NOT_FOUND:
                    return template.TemplateResponse('/user/edite.html',{'request':request,"status":"Duplicate","user":user,"user_data":user_data})
                    # return responses.RedirectResponse(url="/user/edite/"+user.id+"/"+"Duplicate")
                else:
                    return responses.RedirectResponse(url="/user/edite/"+data["id"]+"/"+"fasle",status_code=303)
            except Exception as e:
                if attemp < 3 :
                    await asyncio.sleep(1)
                else:
                   return {"error :", e}







@router.get("/user/delete/{itemid}",response_class=HTMLResponse)
async def delete(itemid:str,request:Request):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    if user_data["type"] != "0":
        return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    url = 'http://127.0.0.1:8001/user/delete/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            return responses.RedirectResponse(url="/index/user")
        else:
            return responses.RedirectResponse(url="/index/user")