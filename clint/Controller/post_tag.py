from fastapi import FastAPI,Request,Form,status,Response,Depends,HTTPException,Cookie,responses,File,UploadFile
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import User
from Model import Post
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
TAG_IMG_DIR = "static/tag_img"
os.makedirs(TAG_IMG_DIR, exist_ok=True)


def save_file(UPLOAD_DIR:str,file:UploadFile)->str:
    # تولید اسم یونیک برای عکس
    ext = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    # ذخیره عکس
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return filename



@router.get("/post/tag/index",response_class=HTMLResponse)
async def post_tag(request:Request,response: Response):

    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    if user_data["type"] != "0":
        return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    # return"sssss"
    url = 'http://127.0.0.1:8001/post/tag/index'  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            tags=response.json()
            # return str(tags)
            return template.TemplateResponse('post_tag/index.html',{'request':request,"status":"ok","tags":tags,"user_data":user_data})
        else:
            # return "resssss"
            return RedirectResponse(url="/login")

@router.get("/post/tag/create",response_class=HTMLResponse)
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
    return template.TemplateResponse('post_tag/create.html',{'request':request,"user_data":user_data})



@router.post("/post/tag/create",response_class=HTMLResponse)
async def create(request:Request,response: Response,
img_upload: UploadFile = File(None),
tag:str=Form(...)):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    if user_data["type"] != "0":
        return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    tag_objectt=Post.Tag(tag=tag,img="defult_tag.png")
    if img_upload and img_upload.filename !="":
        tag_objectt.img=save_file(TAG_IMG_DIR,img_upload)
    else:
        tag_objectt.img="defult_tag.png"
    data=tag_objectt.dict()
    # return str(data)
    url = 'http://127.0.0.1:8001/post/tag/create'  # آدرس URL
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
                    return template.TemplateResponse('/post_tag/create.html',{'request':request,"status":"ok","user_data":user_data})
                
                else:
                    return template.TemplateResponse('/post_tag/create.html',{'request':request,"status":"flase","user_data":user_data}) 
            except Exception as e:
                if attemp < 3 :
                    await asyncio.sleep(1)
                else:
                   return {"error :", e}






@router.get("/post/tag/delete/{itemid}",response_class=HTMLResponse)
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
    url = 'http://127.0.0.1:8001/post/tag/detail/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers,timeout=10)
        if response.status_code == status.HTTP_200_OK:
            old_tag=response.json()
        else:
            return responses.RedirectResponse(url="/post/tag/index")

    if old_tag["img"] != "defult_tag.png":
        try:
            old_path_img=os.path.join(TAG_IMG_DIR,old_tag.img)
            os.remove(old_path_img)
        except:
            pass

    url = 'http://127.0.0.1:8001/post/tag/delete/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            return responses.RedirectResponse(url="/post/tag/index")
        else:
            return responses.RedirectResponse(url="/post/tag/index")