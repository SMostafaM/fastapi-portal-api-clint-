from fastapi import FastAPI,Header,HTTPException,status
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import Notife,Interaction
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
notife_collection = db.get_collection("notife")
post_collection = db.get_collection("post")
like_collectiom=db.get_collection("like")
notif_comment_collectiom=db.get_collection("notif_comment")
post_comment_collectiom=db.get_collection("post_comment")
deleted_comment_collectiom=db.get_collection("deleted_comment")
# active_collection = db.get_collection("active_session")
log_collection = db.get_collection("log")

def convert_mongo_to_json(item):
    if isinstance(item, dict):
        return {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in item.items()}
    return item

def fixid(user):
    user["_id"]=str(user["_id"])
    return user

# @router.get("/like")
# async def like(Xtoken: str = Header(""),Ujtoken:str=Header("")):
#     # print ("like","+++++++++++++++++++++++++++++++++get")

@router.post("/like/{type_like}/{count_like}")
async def like(type_like:str,count_like:str,like:Interaction.like_insert,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        like_di=like.dict()
        like_exist=await like_collectiom.find_one(like_di)
        
        bson_id=ObjectId(like.post_id)
        #dislike
        # if like_exist !=None:
        l_c=count_like
        if like_exist !=None and type_like =="dislike":
            # print ("like","+++++++++++++++++++++++++++++++++dislike")
            await like_collectiom.delete_one(like_di)
            log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"like","subject":"remove","object":like_di})
            if like.type_post=="notif":
                notif= await notife_collection.find_one({"_id":bson_id})
                l_c=int(notif["count_like"])-1
                notife_collection.update_one({"_id":bson_id},{"$set":{"count_like":l_c}})
            elif like.type_post=="post":
                post= await post_collection.find_one({"_id":bson_id})
                l_c=int(post["count_like"])-1
                post_collection.update_one({"_id":bson_id},{"$set":{"count_like":l_c}})
        #like
        elif like_exist == None and type_like =="like":
            # print ("like","+++++++++++++++++++++++++++++++++insert")
            now_shamsi=jdatetime.datetime.now()
            true_date_str=now_shamsi.strftime("%Y-%m-%d %H:%M")
            like_di["date"]=true_date_str
            await like_collectiom.insert_one(like_di)
            log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"like","subject":"add","object":like_di})
            if like.type_post=="notif":
                notif= await notife_collection.find_one({"_id":bson_id})
                l_c=int(notif["count_like"])+1
                notife_collection.update_one({"_id":bson_id},{"$set":{"count_like":l_c}})
            elif like.type_post=="post":
                post= await post_collection.find_one({"_id":bson_id})
                l_c=int(post["count_like"])+1
                post_collection.update_one({"_id":bson_id},{"$set":{"count_like":l_c}})

        # print ("like","+++++++++++++++++++++++++++++++++show",str(like_exist),type_like,l_c)
        return str(l_c)
        # raise HTTPException(status_code=status.HTTP_200_OK,detail="inserted",content=str(l_c))
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)

@router.post("/comment/insert")
async def comment_insert(comment:Interaction.comment,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        now_shamsi=jdatetime.datetime.now()
        true_date_str=now_shamsi.strftime("%Y-%m-%d %H:%M")

        comment_di=comment.dict()
        comment_di["date"]=true_date_str
        bson_id=ObjectId(comment.post_id)
        #dislike
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"commetn","subject":"insert","object":comment_di})
        if comment.type_post=="notif":
            await notif_comment_collectiom.insert_one(comment_di)
            notif= await notife_collection.find_one({"_id":bson_id})
            l_c=int(notif["count_comment"])+1
            notife_collection.update_one({"_id":bson_id},{"$set":{"count_comment":l_c}})
        elif comment.type_post=="post":
            await post_comment_collectiom.insert_one(comment_di)
            post= await post_collection.find_one({"_id":bson_id})
            l_c=int(post["count_comment"])+1
            post_collection.update_one({"_id":bson_id},{"$set":{"count_comment":l_c}})

        raise HTTPException(status_code=status.HTTP_200_OK,detail="inserted")
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/comment/{post_id}/{type_post}/{user}/{self_id}")
async def comment(post_id:str,type_post:str,user:str="all",self_id:str="0",Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"commetn_get","subject":type_post+"**user:"+user,"object":post_id})
        final_list=[]
        # print("++++++++++++++++",post_id,user)
        if type_post=="notif":
            if user == "all":
                comments= notif_comment_collectiom.find({ "$and" : [{"user" : { "$ne" : self_id }}, {"post_id" : post_id}] })
            else:
                comments= notif_comment_collectiom.find({"post_id":post_id,"user":user})

        elif type_post=="post":
            if user == "all":
                comments= post_comment_collectiom.find({ "$and" : [{"user" : { "$ne" : self_id }}, {"post_id" : post_id}] })
            else:
                comments= post_comment_collectiom.find({"post_id":post_id,"user":user})
        
        # for item in comments:
        if user == "all":
            async for item in comments:
                user= await User_collection.find_one({"username":item["user"]})
                item["user_name"]=user["name"]
                item["user_img"]=user["img"]
                item["_id"]=str(item["_id"])
                final_list.append(item)

        else:
            async for item in comments:
                item["_id"]=str(item["_id"])
                user= await User_collection.find_one({"username":user_info_token_username})
                item["user_name"]=user["name"]
                item["user_img"]=user["img"]
                final_list.append(item)
        
        return final_list
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)


@router.delete("/comment/delete/{type_post}/{comment_id}")
async def delete(type_post:str,comment_id:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        
        # comment_di=comment.dict()
        bson_id=ObjectId(comment_id)
        if type_post=="notif":
            comment= await notif_comment_collectiom.find_one({"_id":bson_id})
        elif type_post=="post":
            comment= await post_comment_collectiom.find_one({"_id":bson_id})
        # print("delete comment -+-+-+-+-+-+-+-+-",str(comment))
        bson_id_post=ObjectId(comment["post_id"])
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"commetn_delete","subject":comment['post_id'],"object":comment})
        deleted_comment_collectiom.insert_one(comment)

        if comment["type_post"]=="notif":
            notif= await notife_collection.find_one({"_id":bson_id_post})
            l_c=int(notif["count_comment"])-1
            notife_collection.update_one({"_id":bson_id_post},{"$set":{"count_comment":l_c}})
            notif_comment_collectiom.delete_one({"_id":bson_id})

        elif comment["type_post"]=="post":
            post= await post_collection.find_one({"_id":bson_id_post})
            l_c=int(post["count_comment"])-1
            post_collection.update_one({"_id":bson_id_post},{"$set":{"count_comment":l_c}})
            post_comment_collectiom.find({"_id":bson_id})
            
        return HTTPException(detail="deleted",status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)
        








