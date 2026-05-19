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



@router.get("/notif/index",response_class=HTMLResponse)
async def notif(request:Request,response: Response):

    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # return str(user_data)
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    
    url = 'http://127.0.0.1:8001/notif/index/'+str(user_data["type"])  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            notifs=response.json()
            # return str(users)
            return template.TemplateResponse('notif/index.html',{'request':request,"status":"ok","notifs":notifs,"user_data":user_data})
        else:
            # return "resssss"
            return RedirectResponse(url="/login")

@router.get("/notif/create",response_class=HTMLResponse)
async def create(request:Request):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    # return str(user_data)
    return template.TemplateResponse('notif/create.html',{'request':request,"user_data":user_data})



@router.post("/notif/create",response_class=HTMLResponse)
async def create(request:Request,response: Response,
img_upload: UploadFile = File(None),
attachment_upload:List[UploadFile]=File([]),
moavenat:str=Form(...),
title:str=Form(...),
text:str=Form(...),
show:bool=Form(False),
important:bool=Form(False),
comment:bool=Form(False),
like:bool=Form(False),
secret:bool=Form(False)
):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    # n=img_upload.filename
    # # print(n,"+++++++++++++++")
    # return text
    notif=Notif.Notife_insert(moavenat=moavenat,title=title,text=text,show=show,important=important,comment=comment,like=like,secret=secret,img="defult.jpg")
    if img_upload and img_upload.filename !="":
        notif.img=save_file(NOTIF_IMG_DIR,img_upload)
    else:
        notif.img="defult.jpg"
    if len(attachment_upload)!=0 and attachment_upload[0].filename !="":
        attach_list=[]
        for file in attachment_upload:
            attach_list.append(save_file(NOTIF_ATTACH_DIR,file))
        notif.attachment=attach_list
    else:
        notif.attachment=[]
    data=notif.dict()
    
    # return str(data)
    url = 'http://127.0.0.1:8001/notif/create'  # آدرس URL
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
                    return template.TemplateResponse('/notif/create.html',{'request':request,"status":"ok","user_data":user_data})
                
                else:
                    return template.TemplateResponse('/notif/create.html',{'request':request,"status":"flase","user_data":user_data})
            except Exception as e:
                if attemp < 3 :
                    await asyncio.sleep(1)
                else:
                   return {"error :", e}
                



@router.get("/notif/edite/{itemid}/{status_show}",response_class=HTMLResponse)
@router.get("/notif/edite/{itemid}",response_class=HTMLResponse)
async def edite(itemid:str,request:Request,status_show:str="nothing"):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
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
            # return str(notifs[0])
            # try:
            return template.TemplateResponse('notif/edite.html',{'request':request,"notif":notifs[0],"status":status_show,"user_data":user_data})
            # except:
            #     return responses.RedirectResponse(url="notif/index")
            
        else:
            return responses.RedirectResponse(url="notif/index")




@router.post("/notif/edite",response_class=HTMLResponse)
async def edite(request:Request,response: Response,
img_upload: UploadFile = File(None),
attachment_upload:List[UploadFile]=File([]),
id:str=Form(...),
moavenat:str=Form(...),
title:str=Form(...),
text:str=Form(...),
show:bool=Form(False),
important:bool=Form(False),
comment:bool=Form(False),
like:bool=Form(False),
secret:bool=Form(False)
):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    #گرفتن اطلاعیه قبلی
    url = 'http://127.0.0.1:8001/notif/detail/'+id  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            notifs=response.json()
            old_notif= notifs[0]

            
        else:
            return responses.RedirectResponse(url="/notif/edite/"+id+"/"+"fasle")

    #بارگذاری اطلاعیه جدید

    notif=Notif.Notife_complet(moavenat=moavenat,title=title,text=text,show=show,important=important,comment=comment,like=like,secret=secret,img=old_notif["img"],id=id,attachment=old_notif["attachment"])
    if img_upload and img_upload.filename !="":
        try:
            if post.img != "defult.jpg":
                old_path_img=os.path.join(NOTIF_IMG_DIR,notif.img)
                os.remove(old_path_img)
        except:
            pass
        notif.img=save_file(NOTIF_IMG_DIR,img_upload)
    if len(attachment_upload)!=0 and attachment_upload[0].filename !="":
        for item in notif.attachment:
            try:
                old_path_attach=os.path.join(NOTIF_ATTACH_DIR,item)
                os.remove(old_path_attach)
            except:
                pass
        attach_list=[]
        for file in attachment_upload:
            attach_list.append(save_file(NOTIF_ATTACH_DIR,file))
        notif.attachment=attach_list
    data=notif.dict()
    # return str(data)
    url = 'http://127.0.0.1:8001/notif/edite'  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }
    

    async with httpx.AsyncClient() as client:
        for attemp in range(1,3):
            try:
                response2 = await client.post(url, headers=headers, json=data,timeout=10)
                if response2.status_code == status.HTTP_200_OK:
                    # print("++++++++++++++ redirect ++++++++++++++")
                    return RedirectResponse(url="/notif/index",status_code=status.HTTP_303_SEE_OTHER)
                    # return await index_user(request,response)

                elif  response2.status_code == status.HTTP_404_NOT_FOUND:
                    # print("++++++++++++++ 404 ++++++++++++++")
                    return template.TemplateResponse('/notif/edite.html',{'request':request,"notif":notif})
                    # return responses.RedirectResponse(url="/user/edite/"+user.id+"/"+"Duplicate")
                else:
                    # print("++++++++++++++ else ++++++++++++++")
                    return responses.RedirectResponse(url="/notif/edite/"+data["id"]+"/"+"fasle")
            
            except Exception as e:
                if attemp < 3 :
                    await asyncio.sleep(1)
                else:
                   return {"error :", e}







@router.get("/notif/delete/{itemid}",response_class=HTMLResponse)
async def delete(itemid:str,request:Request):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######


    ######
    #گرفتن اطلاعیه قبلی
    url = 'http://127.0.0.1:8001/notif/detail/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers,timeout=10)
        if response.status_code == status.HTTP_200_OK:
            notifs=response.json()
            # return str(notifs)
            old_notif= notifs[0] 
            # return str(old_notif)
        else:
            return responses.RedirectResponse(url="/notif/index")
    
    if old_notif["img"] != "defult_img.jpg":
        try:
            old_path_img=os.path.join(NOTIF_IMG_DIR,old_notif.img)
            os.remove(old_path_img)
        except:
            pass
    if len(old_notif["attachment"])!=0:
        for item in old_notif["attachment"]:
            try:
                old_path_attach=os.path.join(NOTIF_ATTACH_DIR,item)
                os.remove(old_path_attach)
            except:
                pass
        

    url = 'http://127.0.0.1:8001/notif/delete/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            return responses.RedirectResponse(url="/notif/index")
        else:
            return responses.RedirectResponse(url="/notif/index")




