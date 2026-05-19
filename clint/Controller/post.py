from fastapi import FastAPI,Request,Form,status,Response,Depends,HTTPException,Cookie,responses,File,UploadFile
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import User
from Model import Post
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
POST_IMG_DIR = "static/post_img"
os.makedirs(POST_IMG_DIR, exist_ok=True)

POST_ATTACH_DIR = "static/post_attach"
os.makedirs(POST_ATTACH_DIR, exist_ok=True)

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

@router.get("/post/index/admin",response_class=HTMLResponse)
async def post(request:Request,response: Response):
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
    url = 'http://127.0.0.1:8001/post/index/admin/all/0' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            main_post_list=response.json()
            return template.TemplateResponse('post/index_admin.html',{'request':request,"status":"ok","main_post_list":main_post_list,"user_data":user_data})
        else:
            main_post_list=[]

    if response.status_code == status.HTTP_200_OK:
        notifs=response.json()
            # return str(users)
        return template.TemplateResponse('notif/index.html',{'request':request,"status":"ok","notifs":notifs,"user_data":user_data})
    else:
        # return "resssss"
        return RedirectResponse(url="/login")



@router.get("/post/show/{itemid}",response_class=HTMLResponse)
async def post_show(itemid:str,request:Request,response: Response):

    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    if user_data["type"] != "0":
        return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    
    url = 'http://127.0.0.1:8001/post/show/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            members=response.json()
            # return str(users)
            return RedirectResponse(url="/post/index/admin")
        else:
            # return "resssss"
            return RedirectResponse(url="/login")

@router.get("/post/index/{type_req}/{data}/{page}",response_class=HTMLResponse)
@router.get("/post/index/all/{page}",response_class=HTMLResponse)
async def post(request:Request,response: Response,type_req:str="all",data:str="all",page:int=1):
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
    ,'http://127.0.0.1:8001/post/count/'+type_req+"/"+data#تعداد صفحات
    ,'http://127.0.0.1:8001/post/index/'+type_req+"/"+data+"/"+str(page)  #آگهی ها اصلی
    ,'http://127.0.0.1:8001/index/notif?show=True&important=True' # آگهی های مهم
    ,'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True'  #ثبت نام ها
    , 'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' #نظر سنجی ها
    ,'http://127.0.0.1:8001/index/tag' #تگ ها
    ,'http://127.0.0.1:8001/post/tag/index'
    ] # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient(headers=headers) as client:
        tasks=[fetch_url(client,u,request)for u in urls]
        results =await asyncio.gather(*tasks)
    moavenat_list,page_count,main_post_list,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list,tags=results  

    try:
        page_count=int(page_count)+9    
        page_count=page_count//10
    except:
        page_count=1
    # return str(tags)
    return template.TemplateResponse('post/index.html',{'request':request,"tags":tags,"page":page,"user_data":user_data,"main_post_list":main_post_list,"type_req":type_req,"data":data,"page":page,"page_count":page_count,"tag_list":tag_list,"sinup_show_list":sinup_show_list,"survay_show_list":survay_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})


@router.get("/post/index/{type_req}/{data}/{page}/old",response_class=HTMLResponse)
@router.get("/post/index/all/{page}/old",response_class=HTMLResponse)
async def post(request:Request,response: Response,type_req:str="all",data:str="all",page:int=1):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    # ujtoken=create_username_token({"username":"public"})
    ######
    #دریافت آگهی ها
    url = 'http://127.0.0.1:8001/post/index/'+type_req+"/"+data+"/"+str(page) # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            main_post_list=response.json()
            # return str(main_post_list)
        else:
            main_post_list=[]


    #تعداد صفحات آگهی 
    url = 'http://127.0.0.1:8001/post/count/'+type_req+"/"+data # آدرس URL
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

    return template.TemplateResponse('post/index.html',{'request':request,"page":page,"user_data":user_data,"main_post_list":main_post_list,"type_req":type_req,"data":data,"page":page,"page_count":page_count,"tag_list":tag_list,"sinup_show_list":sinup_show_list,"survay_show_list":survay_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})



@router.get("/post/create/{status_info}",response_class=HTMLResponse)
@router.get("/post/create",response_class=HTMLResponse)
async def create(request:Request,status_info:str="nothing"):
        #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    # ujtoken=create_username_token({"username":"public"})
    ######

    urls = ['http://127.0.0.1:8001/post/tag/index' #برچسب های آگهی همون تگ
    ,'http://127.0.0.1:8001/index/moavenat/list' #لیست معاونت ها
    ,'http://127.0.0.1:8001/index/notif?show=True&important=True' # آگهی های مهم ادمین
    ,'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True'  #ثبت نام ها
    , 'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' #نظر سنجی ها
    ,'http://127.0.0.1:8001/index/tag',
    ] # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient(headers=headers) as client:
        tasks=[fetch_url(client,u,request)for u in urls]
        results =await asyncio.gather(*tasks)
    tags,moavenat_list,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list=results  


    return template.TemplateResponse('post/create.html',{'request':request,"tags":tags,"status_info":status_info,"user_data":user_data,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})



@router.get("/post/create/{status_info}/old",response_class=HTMLResponse)
@router.get("/post/create/old",response_class=HTMLResponse)
async def create(request:Request,status_info:str="nothing"):
        #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    # ujtoken=create_username_token({"username":"public"})
    ######
    # return (status_info)


    #برچسب های آگهی همون تگ
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
            # return (str(tags))
        else:
            tags=[]

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

    return template.TemplateResponse('post/create.html',{'request':request,"tags":tags,"status_info":status_info,"user_data":user_data,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})




@router.post("/post/create",response_class=HTMLResponse)
async def create(request:Request,response: Response,
img_upload: UploadFile = File(None),
attachment_upload:List[UploadFile]=File([]),
title:str=Form(...),
text:str=Form(...),
username:str=Form(...),
tag:List[str]=Form(...),
show:bool=Form(False),
comment:bool=Form(False),
like:bool=Form(False)
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
    # # return n
    post=Post.Post_insert(username=username,title=title,text=text,show=show,tag=tag,comment=comment,like=like,img="defult_img.jpg")
    if img_upload and img_upload.filename !="":
        post.img=save_file(POST_IMG_DIR,img_upload)
    else:
        post.img="defult_img.jpg"

    if len(attachment_upload)!=0 and attachment_upload[0].filename !="":
        attach_list=[]
        for file in attachment_upload:
            attach_list.append(save_file(POST_ATTACH_DIR,file))
        post.attachment=attach_list
    else:
        post.attachment=[]
    data=post.dict()
    
    # return str(data)
    url = 'http://127.0.0.1:8001/post/create'  # آدرس URL
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
                    # form_data=response.json()
                    # return str(form_data)
                    status_info="ok"
                else:
                    form_data={}
                    status_info="false"
                    # return str(response.content)
                url="/post/create/"+status_info
                return responses.RedirectResponse(url=url,status_code=303)
            except Exception as e:
                if attemp < 3 :
                    await asyncio.sleep(1)
                else:
                   return {"error :", e}



@router.get("/post/edite/{itemid}/{status_show}",response_class=HTMLResponse)
@router.get("/post/edite/{itemid}",response_class=HTMLResponse)
async def edite(itemid:str,request:Request,status_show:str="nothing"):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    # ujtoken=create_username_token({"username":"public"})
    ######

    urls = ['http://127.0.0.1:8001/post/detail/'+itemid
    ,'http://127.0.0.1:8001/post/tag/index' #برچسب های آگهی همون تگ
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
    post,tags,moavenat_list,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list=results  
    # return str(post)
    status_info=status_show
    return template.TemplateResponse('post/edite.html',{'request':request,"post":post,"tags":tags,"status_info":status_info,"user_data":user_data,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})





@router.post("/post/edite",response_class=HTMLResponse)
async def edite(request:Request,response: Response,
img_upload: UploadFile = File(None),
attachment_upload:List[UploadFile]=File([]),
id:str=Form(...),
title:str=Form(...),
text:str=Form(...),
username:str=Form(...),
tag:List[str]=Form(...),
show:bool=Form(False),
comment:bool=Form(False),
like:bool=Form(False)
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
    url = 'http://127.0.0.1:8001/post/detail/'+id # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            old_post=response.json()

        else:
            return responses.RedirectResponse(url="/post/index/username/"+user_data["username"]+"/1")


    #بارگذاری اطلاعیه جدید
    # return str(tag)
    post=Post.Post_complet(username=username,title=title,text=text,show=show,tag=tag,comment=comment,like=like,img=old_post["img"],id=id,attachment=old_post["attachment"])
    if img_upload and img_upload.filename !="" :
        try:
            if post.img != "defult_img.jpg":
                old_path_img=os.path.join(POST_IMG_DIR,post.img)
                os.remove(old_path_img)
        except:
            pass
        post.img=save_file(POST_IMG_DIR,img_upload)

    if len(attachment_upload)!=0 and attachment_upload[0].filename !="":
        for item in post.attachment:
            try:
                old_path_attach=os.path.join(POST_ATTACH_DIR,item)
                os.remove(old_path_attach)
            except:
                pass
        attach_list=[]
        for file in attachment_upload:
            attach_list.append(save_file(POST_ATTACH_DIR,file))
        post.attachment=attach_list
    data=post.dict()
    # return str(data)
    url = 'http://127.0.0.1:8001/post/edite'  # آدرس URL
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
                    return RedirectResponse(url="/post/edite/"+id+"/ok",status_code=status.HTTP_303_SEE_OTHER)
                    # return await index_user(request,response)

                elif  response2.status_code == status.HTTP_404_NOT_FOUND:
                    # print("++++++++++++++ 404 ++++++++++++++")
                    return RedirectResponse(url="/post/edite/"+id+"/false",status_code=status.HTTP_303_SEE_OTHER)
                    # return responses.RedirectResponse(url="/user/edite/"+user.id+"/"+"Duplicate")
                else:
                    # print("++++++++++++++ else ++++++++++++++")
                    return RedirectResponse(url="/post/edite/"+id+"/ok",status_code=status.HTTP_303_SEE_OTHER)
            except Exception as e:
                if attemp < 3 :
                    await asyncio.sleep(1)
                else:
                   return {"error :", e}







@router.get("/post/delete/{itemid}/{page}",response_class=HTMLResponse)
async def delete(itemid:str,page:str,request:Request):
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
    url = 'http://127.0.0.1:8001/post/detail/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            post=response.json()
            # return str(notifs)
            old_post= post 
            # return str(old_notif)
        else:
            return responses.RedirectResponse(url="/notif/index")
    
    if old_post["img"] != "defult_img.jpg":
        try:
            old_path_img=os.path.join(NOTIF_IMG_DIR,old_post.img)
            os.remove(old_path_img)
        except:
            pass
    if len(old_post["attachment"])!=0:
        for item in old_post["attachment"]:
            try:
                old_path_attach=os.path.join(NOTIF_ATTACH_DIR,item)
                os.remove(old_path_attach)
            except:
                pass
        

    url = 'http://127.0.0.1:8001/post/delete/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            if page !="admin":
                return responses.RedirectResponse(url="/post/index/username/"+user_data["username"]+"/"+page)
            else:
                return responses.RedirectResponse(url="/post/index/admin")
        else:
            if page !="admin":
                return responses.RedirectResponse(url="/post/index/username/"+user_data["username"]+"/"+page)
            else:
                return responses.RedirectResponse(url="/post/index/admin")



@router.get("/post/single/{itemid}",response_class=HTMLResponse)
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
    ,'http://127.0.0.1:8001/comment/'+itemid+'/post/all/'+user_data["username"] #کل کامنت ها به جز کامنت شخص
    ,'http://127.0.0.1:8001/comment/'+itemid+'/post/'+user_data["username"]+'/0' #کامنت های شخص زیر پست
    ,'http://127.0.0.1:8001/index/notif?show=True&important=True' # آگهی های مهم ادمین
    ,'http://127.0.0.1:8001/index/form?type_form=ثبت‌نام&show=True'  #ثبت نام ها
    , 'http://127.0.0.1:8001/index/form?type_form=نظرسنجی&show=True' #نظر سنجی ها
    ,'http://127.0.0.1:8001/index/tag' #تگ ها
    ,'http://127.0.0.1:8001/post/detail/'+itemid
    ,'http://127.0.0.1:8001/post/tag/index'  #گرفتن آکهی 
    ] # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient(headers=headers) as client:
        tasks=[fetch_url(client,u,request)for u in urls]
        results =await asyncio.gather(*tasks)
    moavenat_list,all_comment,user_comment,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list,post,tags=results  

    #گرفتن آکهی
    url = 'http://127.0.0.1:8001/user/detail/username/'+post['username']  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            user_psot=response.json()
        else:
            user_psot={"img":"defult_user.jpg"}

    return template.TemplateResponse('post/post_single.html',{'request':request,"user_post":user_psot,"tags":tags,"post":post,"user_data":user_data,"all_comment":all_comment,"user_comment":user_comment,"tag_list":tag_list,"sinup_show_list":sinup_show_list,"survay_show_list":survay_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})

@router.get("/post/single/{itemid}/old",response_class=HTMLResponse)
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


    #گرفتن آکهی
    url = 'http://127.0.0.1:8001/post/detail/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            post=response.json()
        else:
            post={}


    #کل کامنت ها به جز کامنت شخص
    url = 'http://127.0.0.1:8001/comment/'+itemid+'/post/all/'+user_data["username"] # آدرس URL
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
    url = 'http://127.0.0.1:8001/comment/'+itemid+'/post/'+user_data["username"]+'/0' # آدرس URL
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

    return template.TemplateResponse('post/post_single.html',{'request':request,"post":post,"user_data":user_data,"all_comment":all_comment,"user_comment":user_comment,"tag_list":tag_list,"sinup_show_list":sinup_show_list,"survay_show_list":survay_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})
