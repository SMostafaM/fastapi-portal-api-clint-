from fastapi import FastAPI,Header,HTTPException,status,Body
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import Sinup
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import datetime
import jwt
import jdatetime



# کلید مخفی برای ارسال نام کاربری در هدر درخواست ها
SECRET_KEY_USERNAME = "0041e6ad98c3ae252d"
ALGORITHM_USERNAME = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES_USERNAME = 5

# ایجاد یک router جدید
router = APIRouter()

# اتصال به MongoDB
# client = AsyncIOMotorClient('mongodb://localhost:27017')
# db = client.portal
db = request.app.state.db
User_collection = db.get_collection("Users")
form_collection = db.get_collection("form")
form_collection_rm = db.get_collection("form_removed")
sinup_collection = db.get_collection("sinup")
sinup_collection_rm = db.get_collection("sinup_removed")
log_collection = db.get_collection("log")
member_collection = db.get_collection("member")



# تعریف تابع راه‌اندازی
# @router.on_event("startup")
# async def startup_event():
#     # اطمینان از ایجاد ایندکس TTL فقط یک بار در راه‌اندازی سرور
#     await verificate_collection.create_index("createdAt", expireAfterSeconds=90)


def fixid(user):
    user["_id"]=str(user["_id"])
    return user

@router.get("/form/index/{type_user}")
async def index(Xtoken: str = Header(""),Ujtoken:str=Header(""),type_user:str="0"):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        if type_user =="0":
            forms= form_collection.find({}).sort("_id",-1)
        else:
            forms= form_collection.find({"moavenat":type_user}).sort("_id",-1)

        # notifes_list = await notifes.to_list(length=None)
        forms_list=[]
        async for form in forms:
            form=fixid(form)
            count_person=await sinup_collection.count_documents({"form_id":form["_id"]})
            form["count_person"]=count_person
            forms_list.append(form)

        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"index","subject":"form","object":type_user})
        return forms_list
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/form/detail/{itemid}")
async def detail(itemid:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        # print("id -*+*+-*-*-*-*-*-*-++++*",itemid)
        id=ObjectId(itemid)
        form= await form_collection.find_one({"_id":id})
        # fromes_list = await fromes.to_list(length=None)
        # fromes_list=[]
        # async for frome in fromes:
        #     fromes_list.append(fixid(frome))
        form=fixid(form)
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"detail","subject":"form","object":itemid})
        return form
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)

@router.get("/form/show/{itemid}")
async def detail(itemid:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        # print("id -*+*+-*-*-*-*-*-*-++++*",itemid)
        id=ObjectId(itemid)
        forms= form_collection.find({"_id":id},{"show":1}).sort("_id",-1)
        # fromes_list = await fromes.to_list(length=None)
        async for form in forms:
            if form["show"] ==True:
                form_collection.update_one({"_id":form["_id"]},{"$set":{"show":False}})
                log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"False","subject":"form","object":itemid})

            else:
                form_collection.update_one({"_id":form["_id"]},{"$set":{"show":True}})
                log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"True","subject":"form","object":itemid})

        raise HTTPException(status_code=status.HTTP_200_OK,detail="changed")
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)

@router.post("/form/create")
async def create(from_data:Sinup.FormCreate_insert,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        # print ("nnnn","-------------------------------")

        n_dict=from_data.dict()
        # print (n_dict,"-------------------------------")

        now_shamsi=jdatetime.datetime.now()
        true_date_str=now_shamsi.strftime("%Y-%m-%d %H:%M")
        n_dict["date"]=true_date_str

        n_dict["fields"].append({
            "label": "نام کاربری",
            "type": "text",
            "required": True,
            "options": None
        })

        result=await form_collection.insert_one(n_dict)
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"craete","subject":"form","object":n_dict})
        raise HTTPException(status_code=status.HTTP_200_OK,detail="inserted")
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)

@router.post("/form/edite")
async def edite(from_data:Sinup.FormCreate,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        old_item=await form_collection.find_one({"_id":ObjectId(from_data.id)})
        
        # print(notife)
        form_d=from_data.dict()
        form_d["_id"]=ObjectId(form_d["id"])
        del form_d["id"]
            
        await form_collection.delete_one({"_id":ObjectId(notife.id)})

        now_shamsi=jdatetime.datetime.now()
        true_date_str=now_shamsi.strftime("%Y-%m-%d %H:%M")
        notif_d["date"]=true_date_str

        await form_collection.insert_one(notif_d)
        await log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"edite_form","subject":from_data.dict(),"object":old_item})
        raise HTTPException(status_code=status.HTTP_200_OK,detail="edited")

    else:
        # print("************************** bad **************************")
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)



@router.delete("/form/delete/{itemid}")
async def delete(itemid:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        id=ObjectId(itemid)
        old_item=await form_collection.find_one({"_id":id})
        form_collection.delete_one({"_id":id})
        form_collection_rm.insert_one(old_item)
        sinup_perv=sinup_collection.find({"form_id":itemid})
        sinup_collection_rm.insert_many(sinup_perv)
        sinup_collection.delete_many({"form_id":itemid})
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"delete","subject":"form","object":old_item})
        return HTTPException(detail="deleted",status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)

@router.delete("/member/delete/{itemid}")
async def member_delete(itemid:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        id=ObjectId(itemid)
        old_item=await sinup_collection.find_one({"_id":id})
        sinup_collection.delete_one({"_id":id})
        sinup_collection_rm.insert_one(old_item)

        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"delete","subject":"sinup","object":old_item})
        return HTTPException(detail="deleted",status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)

@router.get("/sinup/member/{itemid}")
async def index(itemid:str,Xtoken: str = Header(""),Ujtoken:str=Header(""),type_user:str="0"):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        # id=ObjectId(itemid)
        members= sinup_collection.find({"form_id":itemid})
        # notifes_list = await notifes.to_list(length=None)
        members_list=[]
        async for person in members:
            members_list.append(fixid(person))

        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"member","subject":"form_id","object":itemid})
        return members_list
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/sinup/user/check/{itemid}/{username}")
async def index(itemid:str,username:str,Xtoken: str = Header(""),Ujtoken:str=Header(""),type_user:str="0"):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        # id=ObjectId(itemid)
        sinuped=await sinup_collection.find_one({"form_id":itemid,"data.نام کاربری":username})
        # notifes_list = await notifes.to_list(length=None)
        if sinuped == None:
            sinuped="not_found"
        else:
            sinuped=fixid(sinuped)
        # members_list=[]
        # async for person in members:
        #     members_list.append(fixid(person))

        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"sinup_check","subject":itemid,"object":username})
        return sinuped
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)

@router.post("/sinup/user")
async def create(from_data:Sinup.SubmissionCreate,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        # print ("nnnn","-------------------------------")

        n_dict=from_data.dict()
        

        now_shamsi=jdatetime.datetime.now()
        true_date_str=now_shamsi.strftime("%Y-%m-%d %H:%M")
        n_dict["date"]=true_date_str
        # print (n_dict,"-------------------------------")

        
        result=await sinup_collection.insert_one(n_dict)
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"sinup","subject":"form","object":n_dict})
        raise HTTPException(status_code=status.HTTP_200_OK,detail="inserted")
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/sinup/user/edite")
async def edite_sinup(from_data:Sinup.SubmissionCreate,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        # print ("nnnn","-------------------------------")

        n_dict=from_data.dict()
        

        now_shamsi=jdatetime.datetime.now()
        true_date_str=now_shamsi.strftime("%Y-%m-%d %H:%M")
        n_dict["date"]=true_date_str
        # print (n_dict,"-------------------------------")

        
        await sinup_collection.delete_one({"form_id":n_dict["form_id"],"data.نام کاربری":n_dict["data"]["نام کاربری"]})
        result=await sinup_collection.insert_one(n_dict)
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"sinup","subject":"form","object":n_dict})
        raise HTTPException(status_code=status.HTTP_200_OK,detail="inserted")
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)