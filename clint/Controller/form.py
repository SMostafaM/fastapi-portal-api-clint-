from fastapi import FastAPI,Request,Form,status,Response,Depends,HTTPException,Cookie,responses,File,UploadFile
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import User
from Model import Form as Form_arch
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
FORM_FILE_DIR = "static/form_archive"
os.makedirs(FORM_FILE_DIR, exist_ok=True)


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

@router.get("/form/index/admin",response_class=HTMLResponse)
async def form(request:Request,response: Response):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    if user_data["type"] != "0":
        return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    # ujtoken=create_username_token({"username":"public"})
    ######
    #دریافت آگهی ها
    url = 'http://127.0.0.1:8001/form/index/admin/all/0' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            main_form_list=response.json()
            return template.TemplateResponse('form/index_admin.html',{'request':request,"status":"ok","main_form_list":main_form_list,"user_data":user_data})
        else:
            main_form_list=[]

    if response.status_code == status.HTTP_200_OK:
        notifs=response.json()
            # return str(users)
        return template.TemplateResponse('notif/index.html',{'request':request,"status":"ok","notifs":notifs,"user_data":user_data})
    else:
        # return "resssss"
        return RedirectResponse(url="/login")




@router.get("/form/archive/index/{type_req}/{data}/{page}",response_class=HTMLResponse)
@router.get("/form/archive/index/all/{page}",response_class=HTMLResponse)
async def form(request:Request,response: Response,type_req:str="all",data:str="all",page:int=1):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    # ujtoken=create_username_token({"username":"public"})
    ######

    page=int(page)
    urls = ['http://127.0.0.1:8001/index/moavenat/list' #لیست معاونت ها
    ,'http://127.0.0.1:8001/form/count/'+type_req+"/"+data#تعداد صفحات
    ,'http://127.0.0.1:8001/form/index/'+type_req+"/"+data+"/"+str(page)  #آگهی ها اصلی
    ,'http://127.0.0.1:8001/index/notif?show=True&important=True' # آگهی های مهم
    ,'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True'  #ثبت نام ها
    , 'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' #نظر سنجی ها
    ,'http://127.0.0.1:8001/index/tag' #تگ ها
    ,'http://127.0.0.1:8001/form/group/index'
    ] # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient(headers=headers) as client:
        tasks=[fetch_url(client,u,request)for u in urls]
        results =await asyncio.gather(*tasks)
    moavenat_list,page_count,main_form_list,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list,groups=results  

    try:
        page_count=int(page_count)+9    
        page_count=page_count//10
    except:
        page_count=1
    # return str(tags)
    return template.TemplateResponse('form_arch/index.html',{'request':request,"groups":groups,"page":page,"user_data":user_data,"main_form_list":main_form_list,"type_req":type_req,"data":data,"page":page,"page_count":page_count,"tag_list":tag_list,"sinup_show_list":sinup_show_list,"survay_show_list":survay_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})



@router.get("/form/archive/create",response_class=HTMLResponse)
async def create(request:Request):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
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
            return template.TemplateResponse('form_arch/create.html',{'request':request,"user_data":user_data,"groups":groups})
        else:
            # return "resssss"
            return RedirectResponse(url="/login")

    # return str(user_data)
    



@router.post("/form/archive/create",response_class=HTMLResponse)
async def create(request:Request,response: Response,
img_upload: UploadFile = File(None),
attachment_upload:List[UploadFile]=File([]),
group:str=Form(...),
title:str=Form(...),
text:str=Form(...),
):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    
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
        else:
            groups=[]



    form_data=Form_arch.Form_insert(group=group,title=title,text=text,img="defult.jpg")
    if img_upload and img_upload.filename !="":
        form_data.img=save_file(FORM_FILE_DIR,img_upload)
    else:
        form_data.img="defult.jpg"
    if len(attachment_upload)!=0 and attachment_upload[0].filename !="":
        attach_list=[]
        for file in attachment_upload:
            attach_list.append(save_file(FORM_FILE_DIR,file))
        form_data.attachment=attach_list
    else:
        form_data.attachment=[]
    data=form_data.dict()
    
    # return str(data)
    url = 'http://127.0.0.1:8001/form/archive/create'  # آدرس URL
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
                    return template.TemplateResponse('/form_arch/create.html',{'request':request,"status":"ok","user_data":user_data,"groups":groups})
                else:
                    return template.TemplateResponse('/form_arch/create.html',{'request':request,"status":"false","user_data":user_data,"groups":groups})
            except Exception as e:
                if attemp < 3 :
                    await asyncio.sleep(1)
                else:
                   return {"error :", e}



@router.get("/form/archive/delete/{itemid}/{type_req}/{data}/{page}",response_class=HTMLResponse)
async def delete(request:Request,itemid:str,type_req:str="all",data:str="all",page:str="1"):
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
    url = 'http://127.0.0.1:8001/form/archive/detail/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            form=response.json()
            # return str(notifs)
            old_form= form 
            # return str(old_notif)
        else:
            return responses.RedirectResponse(url="/notif/index")
    
    if old_form["img"] != "defult.jpg":
        try:
            old_path_img=os.path.join(FORM_FILE_DIR,old_form.img)
            os.remove(old_path_img)
        except:
            pass
    if len(old_form["attachment"])!=0:
        for item in old_form["attachment"]:
            try:
                old_path_attach=os.path.join(FORM_FILE_DIR,item)
                os.remove(old_path_attach)
            except:
                pass
        

    url = 'http://127.0.0.1:8001/form/archive/delete/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            return responses.RedirectResponse(url="/form/archive/index/"+type_req+"/"+data+"/"+page)
        else:

            return responses.RedirectResponse(url="/form/archive/index/"+type_req+"/"+data+"/"+page)



@router.get("/form/archive/single/{itemid}",response_class=HTMLResponse)
async def delete(itemid:str,request:Request):
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
    ,'http://127.0.0.1:8001/index/notif?show=True&important=True' # آگهی های مهم ادمین
    ,'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True'  #ثبت نام ها
    , 'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' #نظر سنجی ها
    ,'http://127.0.0.1:8001/index/tag' #تگ ها
    ,'http://127.0.0.1:8001/form/archive/detail/'+itemid
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
    moavenat_list,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list,form,groups=results  

    return template.TemplateResponse('form_arch/form_archive_single.html',{'request':request,"groups":groups,"form":form,"user_data":user_data,"tag_list":tag_list,"sinup_show_list":sinup_show_list,"survay_show_list":survay_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})