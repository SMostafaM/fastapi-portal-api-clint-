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
group_collection = db.get_collection("form_group")
# notife_edited_collection = db.get_collection("notife_edited")
# active_collection = db.get_collection("active_session")
log_collection = db.get_collection("log")

def convert_mongo_to_json(item):
    if isinstance(item, dict):
        return {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in item.items()}
    return item

def fixid(user):
    user["_id"]=str(user["_id"])
    return user

@router.get("/form/group/index")
async def index(Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        
        groups= group_collection.find({})


        # notifes_list = await notifes.to_list(length=None)
        group_list=[]
        async for g in groups:
            group_list.append(fixid(g))

        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"index","subject":"group_list","object":"all"})
        return group_list
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/form/group/detail/{itemid}")
async def detail(itemid:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        print("id -*+*+-*-*-*-*-*-*-++++*",itemid)
        id=ObjectId(itemid)
        group= await group_collection.find_one({"_id":id})
        group=fixid(group)
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"detail","subject":"group","object":itemid})
        return group
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/form/group/create")
async def create(group:Form.FormGroup,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        print("id -*+*+-*-*-*-*-*-*-++++*","inseted")
        result=await group_collection.insert_one(group.dict())
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"craete","subject":"group","object":group.dict()})
        raise HTTPException(status_code=status.HTTP_200_OK,detail="inserted")
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)

# @router.post("/notif/edite")
# async def edite(notife:Notife.Notife_complet,Xtoken: str = Header(""),Ujtoken:str=Header("")):
#     user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
#     user_info_token_username=user_info_token["username"]
#     if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

#         old_item=await notife_collection.find_one({"_id":ObjectId(notife.id)})
#         await notife_collection.delete_one({"_id":ObjectId(notife.id)})
#         # print(notife)
#         notif_d=notife.dict()
#         notif_d["_id"]=ObjectId(notif_d["id"])
#         del notif_d["id"]
#         await notife_collection.insert_one(notif_d)
#         await log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"edite_notife","subject":notife.dict(),"object":old_item})
#         raise HTTPException(status_code=status.HTTP_200_OK,detail="edited")

#     else:
#         print("************************** bad **************************")
#         raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)



@router.delete("/form/group/delete/{itemid}")
async def delete(itemid:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        id=ObjectId(itemid)
        old_item=await group_collection.find_one({"_id":id})
        group_collection.delete_one({"_id":id})

        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"delete","subject":"group","object":old_item})
        return HTTPException(detail="deleted",status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)