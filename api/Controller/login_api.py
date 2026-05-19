from fastapi import FastAPI,Header,HTTPException,status
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import User
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request

# ایجاد یک router جدید
router = APIRouter()

# اتصال به MongoDB
# client = AsyncIOMotorClient('mongodb://localhost:27017')
# db = client.portal
db = request.app.state.db
User_collection = db.get_collection("Users")
active_collection = db.get_collection("active_session")

def convert_mongo_to_json(item):
    if isinstance(item, dict):
        return {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in item.items()}
    return item
def fixid(user):
    user["_id"]=str(user["_id"])
    return user

@router.post("/login")
async def login(user:User.User_login,Xtoken: str = Header("")):
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        # print(user)
        users=User_collection.find({"username":user.username})
        users_list = await users.to_list(length=None)
        # print ("+++++++++++++++++++")
        for item in users_list:
            # print (item,"-----------------")
            if item["password"]==user.password:
                # user_data=convert_mongo_to_json(item)
                item["_id"]=str(item["_id"])
                return JSONResponse(content={"message": "Login successful", "user": item}, status_code=status.HTTP_200_OK)
                # return True
        # return False
        raise HTTPException(detail="bad user",status_code=status.HTTP_404_NOT_FOUND)
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)



@router.post("/insert_active_session")
async def insert_active_session(user:User.Active_session,Xtoken: str = Header("")):
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        await active_collection.delete_many({"username":user.username})
        user_dict=user.dict()
        await active_collection.insert_one(user_dict)

        raise HTTPException(detail="new active session added",status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/remove_active_session")
async def remove_active_session(user:User.Active_session,Xtoken: str = Header("")):
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        await active_collection.delete_many({"username":user.username,"token":user.token})
        raise HTTPException(detail="remove active session",status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)

@router.post("/check_active_session")
async def check_active_session(user:User.Active_session,Xtoken: str = Header("")):
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        users= active_collection.find({"username":user.username,"token":user.token})
        users_list = await users.to_list(length=None)
        if len(users_list)!=0:
            raise HTTPException(detail="ok token",status_code=status.HTTP_200_OK)
        else:
            raise HTTPException(detail="bad token",status_code=status.HTTP_404_NOT_FOUND)
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)







