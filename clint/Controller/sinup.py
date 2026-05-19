from fastapi import FastAPI,Request,Form,status,Response,Depends,HTTPException,Cookie,responses,File,UploadFile
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import User
from Model import Sinup
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
import pandas as pd
import io
from fastapi.responses import StreamingResponse, HTMLResponse
# from main import semaphore
# ایجاد یک router جدید
router = APIRouter()
template=Jinja2Templates(directory="templates")

async def fetch_url(client,url,request):
    semaphore=request.app.state.semaphore
    async with semaphore:
        response=await client.get(url,timeout=10)
        if response.status_code == status.HTTP_200_OK:
            h=response.json()
        else:
            h=[]
        return h

@router.get("/form/index",response_class=HTMLResponse)
async def index(request:Request,response: Response):

    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    
    url = 'http://127.0.0.1:8001/form/index/'+str(user_data["type"])  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            forms=response.json()
            # return str(users)
            return template.TemplateResponse('sinup/index.html',{'request':request,"status":"ok","forms":forms,"user_data":user_data})
        else:
            # return "resssss"
            return RedirectResponse(url="/login")

# -------------------------
# CREATE FORM
# -------------------------
@router.get("/form/create")
async def create_form(request:Request):
    ##check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    #######
    # return str(user_data)
    return  template.TemplateResponse('sinup/create_form.html',{'request':request,"user_data":user_data})

@router.post("/form/create")
async def create_form(
    request:Request,
    name: str = Form(...),
    moavenat: str = Form(...),
    type_form: str = Form(...),
    show: bool = Form(False),
    fields_json: str = Form(...)
):
    ##check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    #######
    # return name
    fields = json.loads(fields_json)
    schema = Sinup.FormCreate(name=name, type_form=type_form,moavenat=moavenat,show=show, fields=fields)
    # schema = {"name":name, "type_form":type_form,"moavenat":moavenat,"show":show, "fields":fields}
    # result = await collection.insert_one(schema.dict())
    data=schema.dict()
    # return str(data)
    url = 'http://127.0.0.1:8001/form/create'  # آدرس URL
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
                    return template.TemplateResponse('sinup/create_form.html',{'request':request,"status":"ok","user_data":user_data})
                
                else:
                    # return response.content
                    return template.TemplateResponse('sinup/create_form.html',{'request':request,"status":"flase","user_data":user_data}) 
                    
            except Exception as e:
                if attemp < 3 :
                    await asyncio.sleep(1)
                else:
                   return {"error :", e}

   

@router.get("/form/detail/{itemid}",response_class=HTMLResponse)
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
    url = 'http://127.0.0.1:8001/form/detail/'+itemid  # آدرس URL
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
            old_notif= notifs[0] 
            # return str(old_notif)
            return template.TemplateResponse('sinup/detail.html',{'request':request,"notif":notifs[0],"user_data":user_data})
        else:
            return responses.RedirectResponse(url="/from/index")
    




@router.get("/form/delete/{itemid}",response_class=HTMLResponse)
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
    
    url = 'http://127.0.0.1:8001/form/delete/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            return responses.RedirectResponse(url="/form/index")
        else:
            return responses.RedirectResponse(url="/form/index")



@router.get("/member/delete/{person_id}/{form_id}",response_class=HTMLResponse)
async def delete(person_id:str,form_id:str,request:Request):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######


    ######
    
    url = 'http://127.0.0.1:8001/member/delete/'+person_id  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken   # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            return responses.RedirectResponse(url="/form/member/"+form_id)
        else:
            return responses.RedirectResponse(url="/form/member/"+form_id)

@router.get("/form/member/{itemid}",response_class=HTMLResponse)
async def form_member(itemid:str,request:Request,response: Response):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    
    url = 'http://127.0.0.1:8001/sinup/member/'+itemid  # آدرس URL
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
            return template.TemplateResponse('sinup/member.html',{'request':request,"status":"ok","members":members,"user_data":user_data})
        else:
            # return "resssss"
            return RedirectResponse(url="/login")

@router.get("/form/download/member/{itemid}",response_class=HTMLResponse)
async def form_member(itemid:str,request:Request,response: Response):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    
    url = 'http://127.0.0.1:8001/sinup/member/'+itemid  # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            members=response.json()
            exported_list=[]
            for person in members:
                person["data"].update({"زمان ثبت نام":person["date"]})
                exported_list.append(person["data"])
            # return str(exported_list)
            df=pd.DataFrame(exported_list)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            output.seek(0)
            return StreamingResponse(
                        output,
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=users.xlsx"}
                    )

            # return template.TemplateResponse('sinup/member.html',{'request':request,"status":"ok","members":members,"user_data":user_data})
        else:
            # return "resssss"
            return RedirectResponse(url="/login")

@router.get("/form/show/{itemid}",response_class=HTMLResponse)
async def form_show(itemid:str,request:Request,response: Response):

    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    if user_data["type"] != "0":
        return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    ######
    
    url = 'http://127.0.0.1:8001/form/show/'+itemid  # آدرس URL
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
            return RedirectResponse(url="/form/index")
        else:
            # return "resssss"
            return RedirectResponse(url="/login")



@router.get("/sinup/{form_id}/{status_info}",response_class=HTMLResponse)
@router.get("/sinup/insert/{form_id}",response_class=HTMLResponse)
@router.get("/sinup/{form_id}",response_class=HTMLResponse)
async def sinup(request:Request,response: Response,form_id:str,status_info:str="nothing"):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    # ujtoken=create_username_token({"username":"public"})
    ######
    #بررسی وضعیت ثبت نام
    url = 'http://127.0.0.1:8001/sinup/user/check/'+form_id+"/"+user_data["username"]# آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        # if response.status_code == status.HTTP_200_OK:
        user_form_data=response.json()
        if user_form_data != "not_found":
            sinup_type="edite"
        else:
            sinup_type="create"


    urls = ['http://127.0.0.1:8001/form/detail/'+form_id #اطلاعات فرم
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
    form_data,moavenat_list,main_notif_list_admin,sinup_show_list,survay_show_list,tag_list=results  

    return template.TemplateResponse('sinup/sinup.html',{'request':request,"status_info":status_info,"user_form_data":user_form_data,"sinup_type":sinup_type,"form_data":form_data,"user_data":user_data,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})

 
@router.get("/sinup/{form_id}/{status_info}/old",response_class=HTMLResponse)
@router.get("/sinup/insert/{form_id}/old",response_class=HTMLResponse)
@router.get("/sinup/{form_id}/old",response_class=HTMLResponse)
async def sinup(request:Request,response: Response,form_id:str,status_info:str="nothing"):
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
    #بررسی وضعیت ثبت نام
    url = 'http://127.0.0.1:8001/sinup/user/check/'+form_id+"/"+user_data["username"]# آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        # if response.status_code == status.HTTP_200_OK:
        user_form_data=response.json()
        if user_form_data != "not_found":
            sinup_type="edite"
        else:
            sinup_type="create"


   #اطلاعات فرم
    url = 'http://127.0.0.1:8001/form/detail/'+form_id # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        response =await client.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            form_data=response.json()
            # return str(form_data)
        else:
            form_data={}



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

    return template.TemplateResponse('sinup/sinup.html',{'request':request,"status_info":status_info,"user_form_data":user_form_data,"sinup_type":sinup_type,"form_data":form_data,"user_data":user_data,"tag_list":tag_list,"survay_show_list":survay_show_list,"sinup_show_list":sinup_show_list,"moavenats":moavenat_list,"main_notif_list_admin":main_notif_list_admin})

 
 
@router.post("/sinup/insert/{form_id}",response_class=HTMLResponse)
@router.post("/sinup/{sinup_type}/{form_id}",response_class=HTMLResponse)
async def sinup(request:Request,response: Response,form_id:str,sinup_type:str):
    #check cookei
    user_data =await check_token(request)
    if isinstance(user_data,RedirectResponse):
        return user_data
    # if user_data["type"] != "0":
    #     return responses.RedirectResponse(url="/logout")
    ujtoken=create_username_token({"username":user_data["username"]})
    # ujtoken=create_username_token({"username":"public"})
    ######
    status_info=""
    form_data=await request.form()
    form_data_dict=dict(form_data)
    # return str(form_data_dict)

    check_list_key={}
    for item in form_data_dict:
        if "checkserveral" in item:
            list_name=item.split("-")
            check_list_key.update({item:list_name[0]})
            
    
    final_check_list=[]
    for check_key in check_list_key:
        list_ch=form_data.getlist(check_key)
        final_check_list.append({check_list_key[check_key]:list_ch})
        form_data_dict.pop(check_key,None)
    # return (str(final_check_list))

    for item in final_check_list:
        form_data_dict.update(item)

    form_data_dict["نام کاربری"]=user_data["username"]
 
    send_dictionary={"form_id":form_id,"name":form_data_dict["name"],"moavenat":form_data_dict["moavenat"],"type_form":form_data_dict["type_form"]}
    remove_key=["name","moavenat","type_form"]
    for k in remove_key:
        form_data_dict.pop(k,None)
    send_dictionary.update({"data":form_data_dict})
    # return str(send_dictionary)


    #ثبت فرم
    if sinup_type=="create":
        url = 'http://127.0.0.1:8001/sinup/user' # آدرس URL
    else:
        url = 'http://127.0.0.1:8001/sinup/user/edite' # آدرس URL
    headers = {
        'Content-Type': 'application/json',
        'Xtoken': '0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc',
        "Ujtoken":ujtoken  # مثال: هدر احراز هویت
    }
    async with httpx.AsyncClient() as client:
        for attemp in range(1,3):
            try:
                response =await client.post(url, headers=headers,json=send_dictionary,timeout=10)
                if response.status_code == status.HTTP_200_OK:
                    # form_data=response.json()
                    # return str(form_data)
                    status_info="ok"
                else:
                    form_data={}
                    status_info="false"
                    # return str(response.content)
                url="/sinup/"+form_id+"/"+status_info
                return responses.RedirectResponse(url=url,status_code=303)
            except Exception as e:
                if attemp < 3 :
                    await asyncio.sleep(1)
                else:
                   return {"error :", e}


    