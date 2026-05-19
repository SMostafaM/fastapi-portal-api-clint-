from fastapi import FastAPI,Request,Form,status,Response,Depends,HTTPException,Cookie,responses,File,UploadFile
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import User
from Model import Form as Form_model
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


# ایجاد یک router جدید
router = APIRouter()
template=Jinja2Templates(directory="templates")

# اطمینان از وجود دایرکتوری برای ذخیره عکس‌ها
FORM_GROUP_IMG_DIR = "static/from_group_img"
os.makedirs(FORM_GROUP_IMG_DIR, exist_ok=True)


def save_file(UPLOAD_DIR:str,file:UploadFile)->str:
    # تولید اسم یونیک برای عکس
    ext = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    # ذخیره عکس
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return filename



@router.get("/form/group/index",response_class=HTMLResponse)
async def form_group(request:Request,response: Response):

    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    if user_data["type"] != "0":
        return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    # return"sssss"
    url = 'http://127.0.0.1:8001/form/group/index'  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            groups=response.json()
            # return str(groups)
            return template.TemplateResponse('form_group/index.html',{'request':request,"status":"ok","groups":groups,"user_data":user_data})
        else:
            # return "resssss"
            return RedirectResponse(url="/login")

@router.get("/form/group/create",response_class=HTMLResponse)
async def create(request:Request):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    if user_data["type"] != "0":
        return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    # return str(user_data)
    return template.TemplateResponse('form_group/create.html',{'request':request,"user_data":user_data})



@router.post("/form/group/create",response_class=HTMLResponse)
async def create(request:Request,response: Response,
img_upload: UploadFile = File(None),
name:str=Form(...)):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    if user_data["type"] != "0":
        return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    group_objectt=Form_model.FormGroup(name=name,img="defult_group.png")
    if img_upload and img_upload.filename !="":
        group_objectt.img=save_file(FORM_GROUP_IMG_DIR,img_upload)
    else:
        group_objectt.img="defult_group.png"
    data=group_objectt.dict()
    # return str(data)
    url = 'http://127.0.0.1:8001/form/group/create'  # آدرس URL
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
                    return template.TemplateResponse('/form_group/create.html',{'request':request,"status":"ok","user_data":user_data})
                
                else:
                    return template.TemplateResponse('/form_group/create.html',{'request':request,"status":"flase","user_data":user_data}) 
            except Exception as e:
                if attemp < 3 :
                    await asyncio.sleep(1)
                else:
                   return {"error :", e}






@router.get("/form/group/delete/{itemid}",response_class=HTMLResponse)
async def delete(itemid:str,request:Request):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    #گرفتن اطلاعیه قبلی
    url = 'http://127.0.0.1:8001/form/group/detail/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers,timeout=10)
        if response.status_code == status.HTTP_200_OK:
            old_group=response.json()
        else:
            return responses.RedirectResponse(url="/form/group/index")

    if old_group["img"] != "defult_group.png":
        try:
            old_path_img=os.path.join(fORM_GROUP_IMG_DIR,old_group.img)
            os.remove(old_path_img)
        except:
            pass

    url = 'http://127.0.0.1:8001/form/group/delete/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            return responses.RedirectResponse(url="/form/group/index")
        else:
            return responses.RedirectResponse(url="/form/group/index")