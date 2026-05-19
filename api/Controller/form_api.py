from fastapi import FastAPI,Header,HTTPException,status
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import Form
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
form_collection = db.get_collection("form_archive")
form_archive_collection = db.get_collection("form_archive_archive")
form_edited_collection = db.get_collection("form_archive_edited")
# form_comment_collectiom=db.get_collection("form_comment")
# active_collection = db.get_collection("active_session")
log_collection = db.get_collection("log")

def convert_mongo_to_json(item):
    if isinstance(item, dict):
        return {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in item.items()}
    return item

def fixid(user):
    user["_id"]=str(user["_id"])
    return user


@router.get("/form/index/{type_req}/{data}/{page}")
@router.get("/form/index/{type_req}/{page}")
async def index(Xtoken: str = Header(""),Ujtoken:str=Header(""),type_req:str="all",data:str="all",page:int=1):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        page=page-1
        if type_req =="all":
            forms= form_collection.find().sort("_id",-1).skip(page*10).limit(12)
        elif type_req=="admin":
            forms= form_collection.find().sort("_id",-1)
        else:
            forms= form_collection.find({"group":data}).sort("_id",-1).skip(page*10).limit(12)

        # notifes_list = await notifes.to_list(length=None)
        forms_list=[]
        async for form in forms:
            forms_list.append(fixid(form))

        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"index","subject":"form","object":type_req})
        return forms_list
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)



@router.get("/form/count/{type_req}/{data}")
@router.get("/form/count/{type_req}/")
async def form_count(type_req:str="all",data:str="all",Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        if type_req == "all":
            count_form=await form_collection.count_documents({})
        else:
            count_form=await form_collection.count_documents({"group":data})


        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"count_form","subject":type_req,"object":data})
        return count_form
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/form/archive/detail/{itemid}")
async def detail(itemid:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        # print("id -*+*+-*-*-*-*-*-*-++++*",itemid)
        id=ObjectId(itemid)
        form= await form_collection.find_one({"_id":id})
        # notifes_list = await notifes.to_list(length=None)
        form=fixid(form)
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"detail","subject":"form","object":form})
        return form
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/form/archive/create")
async def create(form:Form.Form_insert,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        n_dict=form.dict()
        

        now_shamsi=jdatetime.datetime.now()
        true_date_str=now_shamsi.strftime("%Y-%m-%d %H:%M")
        n_dict["date"]=true_date_str

        n_dict["create_at"]=datetime.datetime.utcnow()

        await form_archive_collection.insert_one(n_dict)
        await form_collection.insert_one(n_dict)
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"craete","subject":"form","object":n_dict})
        raise HTTPException(status_code=status.HTTP_200_OK,detail="inserted")
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)

@router.post("/form/edite")
async def edite(form:Form.Form_complet,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        old_item=await form_collection.find_one({"_id":ObjectId(form.id)})
        
        # print(notife)
        form_d=form.dict()
        form_d["_id"]=ObjectId(form_d["id"])
        del form_d["id"]

        await form_collection.delete_one({"_id":ObjectId(form.id)})

        # now_shamsi=jdatetime.datetime.now()
        # true_date_str=now_shamsi.strftime("%Y-%m-%d %H:%M")
        # form_d["date"]=true_date_str

        await form_collection.insert_one(form_d)
        old_item.update({"id":old_item["_id"]})
        del old_item["_id"]
        await form_edited_collection.insert_one(old_item)

        await log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"form_notife","subject":form.dict(),"object":old_item})
        raise HTTPException(status_code=status.HTTP_200_OK,detail="edited")

    else:
        # print("************************** bad **************************")
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)



@router.delete("/form/archive/delete/{itemid}")
async def delete(itemid:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        id=ObjectId(itemid)
        old_item=await form_collection.find_one({"_id":id})
        form_collection.delete_one({"_id":id})
        # form_collection.delete_many({"form_id":id})
        # form_comment_collectiom.delete_many({"form_id":itemid})
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"delete","subject":"form","object":old_item})
        return HTTPException(detail="deleted",status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)