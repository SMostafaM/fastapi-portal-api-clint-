from fastapi import FastAPI,Header,HTTPException,status
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import User
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
User_collection = db.get_collection("Users")
active_collection = db.get_collection("active_session")
log_collection = db.get_collection("log")

def convert_mongo_to_json(item):
    if isinstance(item, dict):
        return {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in item.items()}
    return item

def fixid(user):
    user["_id"]=str(user["_id"])
    return user

@router.get("/user/index")
async def index(Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        users= User_collection.find({})
        # users_list = await users.to_list(length=None)
        users_list=[]
        async for user in users:
            users_list.append(fixid(user))

        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"index","subject":"user","object":"all_user"})
        return users_list
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/user/detail/{itemid}")
async def detail(itemid:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        id=ObjectId(itemid)
        users= User_collection.find({"_id":id})
        # users_list = await users.to_list(length=None)
        users_list=[]
        async for user in users:
            users_list.append(fixid(user))
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"detail","subject":"user","object":users_list[0]["username"]})
        return users_list
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)

@router.get("/user/detail/username/{username}")
async def detail(username:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        # id=ObjectId(itemid)
        # print("-------------+++++++++++++++",username)
        user= await User_collection.find_one({"username":username})
        user_fixed=fixid(user)
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"detail","subject":"user","object":user["username"]})
        return user_fixed
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/user/create")
async def create(user:User.User_plus,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        exist=await User_collection.find_one({"username":user.username})
        if exist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="dublicate username")

        result=await User_collection.insert_one(user.dict())
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"craete","subject":"user","object":user.dict()})
        raise HTTPException(status_code=status.HTTP_200_OK,detail="inserted")
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)

@router.post("/user/edite")
async def edite(user:User.User_plus_complte,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        old_user=await User_collection.find_one({"_id":ObjectId(user.id)})
        # print(old_user,"***********old")
        # print(user,"***********")
        change_num=0
        l=[]
        # if user.password:
        if user.password!= None and user.password!="" and old_user["password"] != user.password:
            # old_user["password"] = user.password
            old_user["password"] = user.password
            change_num=change_num+1
            l.append("pass")
            

        if user.type_user != old_user["type_user"]:
            old_user["type_user"]=user.type_user
            change_num=change_num+1
            l.append("role")

        if user.name != old_user["name"]:
            old_user["name"]=user.name
            change_num=change_num+1
            l.append("name")
        
        if user.img !="not_new_img":
            old_user["img"]=user.img
            change_num=change_num+1
            l.append("img")


        count_exist_user=0
        if old_user["username"] != user.username:
            count_exist_user=await User_collection.count_documents({"username":user.username})
            change_num=change_num+1
            l.append("user")
            if count_exist_user == 0:
                old_user["username"]=user.username

        # print(l,"*****************",count_exist_user)

        if count_exist_user !=0:
            # print("************************** dublicate **************************")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="dublicate username")

        if change_num > 0 and count_exist_user == 0:
            await User_collection.delete_one({"_id":ObjectId(user.id)})
            await User_collection.insert_one(old_user)
            await log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"edite_user","subject":old_user["type_user"],"object":old_user["username"]})
            # print("************************** edited **************************")
            raise HTTPException(status_code=status.HTTP_200_OK,detail="edited")
        else:
            # print("************************** bad **************************")
            raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)
    else:
        # print("************************** bad **************************")
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)



@router.get("/user/delete/{itemid}")
async def delete(itemid:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        id=ObjectId(itemid)
        old_user=await User_collection.find_one({"_id":id})
        User_collection.delete_one({"_id":id})

        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"delete","subject":"user","object":old_user})
        return HTTPException(detail="deleted",status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)