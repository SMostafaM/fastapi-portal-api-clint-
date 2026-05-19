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
from Model import Interaction
from typing import List
import uuid
import shutil


# ایجاد یک router جدید
router = APIRouter()
template=Jinja2Templates(directory="templates")

# اطمینان از وجود دایرکتوری برای ذخیره عکس‌ها
NOTIF_IMG_DIR = "static/notif_img"
os.makedirs(NOTIF_IMG_DIR, exist_ok=True)

NOTIF_ATTACH_DIR = "static/notif_attach"
os.makedirs(NOTIF_ATTACH_DIR, exist_ok=True)





@router.get("/like/{item_id}/{type_like}/{type_post}/{rev_plac}/{count_like}",response_class=HTMLResponse)
async def notif(request:Request,response: Response,item_id:str,type_post:str,type_like:str,rev_plac:str="index",count_like:str="0"):

    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        # return 
        return "login"
    # return str(user_data)
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    data={"user":user_data["username"],"type_post":type_post,"post_id":item_id}
    
    # return str(data)
    url = 'http://127.0.0.1:8001/like/'+type_like +"/"+count_like # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    # async with httpx.AsyncClient() as client:
    #     response = await client.get(url, headers=headers)
    #     return str(response.content)

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        # return str(response.content)
        if response.status_code == status.HTTP_200_OK:
            count_like=response.json()
            # print ("like_1_+6+6+6+66+6+66+6+66+6+6+6+6+6+6",count_like)
            # return str(users)
            return count_like
        else:
            return "*"
        #     if rev_plac=="index":
        #         url="/index"
        #     elif rev_plac == "single":
        #         url="/"+type_post+"/single/"+item_id
        #     else:
        #         url="/"+type_post+"/"+rev_plac
        #     # return url
        #     return responses.RedirectResponse(url=url)
        # else:
        #     if rev_plac=="index":
        #         url="/index"
        #     elif rev_plac == "single":
        #         url="/"+type_post+"/single/"+item_id
        #     else:
        #         url="/"+type_post+"/"+rev_plac
        #     # return url
        #     return responses.RedirectResponse(url=url)

    
@router.post("/comment",response_class=HTMLResponse)
async def comment(request:Request,response: Response,comment_data:Interaction.Comment=Form(...)):

    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # return str(user_data)
    # if user_data["type"] == "90":
    #     return responses.RedirectResponse(url="/index")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    data=comment_data.dict()
    data["user"]=user_data["username"]

    #check user baned
    url="/"+comment_data.type_post+"/single/"+comment_data.post_id
    if user_data["type"] == "90":
        return responses.RedirectResponse(url=url,status_code=303)


    # return str(data)
    url = 'http://127.0.0.1:8001/comment/insert'  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        # return str(response.content)
        if response.status_code == status.HTTP_200_OK:
            # url="/"+comment_data.type_post+"/single/"+comment_data.post_id
            url="/"+data["type_post"]+"/single/"+data["post_id"]
        else:
            url="/"+comment_data.type_post+"/single/"+comment_data.post_id
        # return url
        return responses.RedirectResponse(url=url,status_code=303)


@router.get("/comment/delete/{type_post}/{post_id}/{comment_id}",response_class=HTMLResponse)
async def comment(request:Request,response: Response,type_post:str,post_id:str,comment_id:str):

    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # return str(user_data)
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    url = 'http://127.0.0.1:8001/comment/delete/'+type_post+"/"+comment_id  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers)
        # return str(response.content)
        if response.status_code == status.HTTP_200_OK:
            # url="/"+comment_data.type_post+"/single/"+comment_data.post_id
            url="/"+type_post+"/single/"+post_id
        else:
            url="/"+type_post+"/single/"+post_id
        # return url
        return responses.RedirectResponse(url=url,status_code=303)

    


    
