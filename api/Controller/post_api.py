from fastapi import FastAPI,Header,HTTPException,status
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import Post
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
post_collection = db.get_collection("post")
post_archive_collection = db.get_collection("post_archive")
post_edited_collection = db.get_collection("post_edited")
post_comment_collectiom=db.get_collection("post_comment")
# active_collection = db.get_collection("active_session")
log_collection = db.get_collection("log")

def convert_mongo_to_json(item):
    if isinstance(item, dict):
        return {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in item.items()}
    return item

def fixid(user):
    user["_id"]=str(user["_id"])
    return user

@router.get("/post/show/{itemid}")
async def detail(itemid:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        # print("id -*+*+-*-*-*-*-*-*-++++*",itemid)
        id=ObjectId(itemid)
        forms= post_collection.find({"_id":id},{"show":1})
        # fromes_list = await fromes.to_list(length=None)
        async for form in forms:
            if form["show"] ==True:
                post_collection.update_one({"_id":form["_id"]},{"$set":{"show":False}})
                log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"False","subject":"post","object":itemid})

            else:
                post_collection.update_one({"_id":form["_id"]},{"$set":{"show":True}})
                log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"True","subject":"post","object":itemid})

        raise HTTPException(status_code=status.HTTP_200_OK,detail="changed")
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)

@router.get("/post/index/{type_req}/{data}/{page}")
@router.get("/post/index/{type_req}/{page}")
async def index(Xtoken: str = Header(""),Ujtoken:str=Header(""),type_req:str="all",data:str="all",page:int=1):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        page=page-1
        if type_req =="all":
            posts= post_collection.find({"show":True}).sort("_id",-1).skip(page*10).limit(10)
        elif type_req=="username":
            posts= post_collection.find({"username":data}).sort("_id",-1).skip(page*10).limit(10)
        elif type_req=="admin":
            posts= post_collection.find().sort("_id",-1)
        else:
            posts= post_collection.find({"show":True,"tag":data}).sort("_id",-1).skip(page*10).limit(10)

        # notifes_list = await notifes.to_list(length=None)
        posts_list=[]
        async for post in posts:
            posts_list.append(fixid(post))

        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"index","subject":"post","object":type_req})
        return posts_list
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)



@router.get("/post/count/{type_req}/{data}")
@router.get("/post/count/{type_req}/")
async def post_count(type_req:str="all",data:str="all",Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        if type_req == "all":
            count_post=await post_collection.count_documents({"show":True})
        elif type_req=="username":
            count_post=await post_collection.count_documents({"username":data})
        else:
            count_post=await post_collection.count_documents({"show":True,"tag":data})


        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"count_post","subject":type_req,"object":data})
        return count_post
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/post/detail/{itemid}")
async def detail(itemid:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        # print("id -*+*+-*-*-*-*-*-*-++++*",itemid)
        id=ObjectId(itemid)
        post= await post_collection.find_one({"_id":id})
        # notifes_list = await notifes.to_list(length=None)
        post=fixid(post)
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"detail","subject":"post","object":post})
        return post
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/post/create")
async def create(post:Post.Post_insert,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        n_dict=post.dict()
        n_dict.update({"count_like":0,"count_comment":0})

        now_shamsi=jdatetime.datetime.now()
        true_date_str=now_shamsi.strftime("%Y-%m-%d %H:%M")
        n_dict["date"]=true_date_str

        n_dict["create_at"]=datetime.datetime.utcnow()

        await post_archive_collection.insert_one(n_dict)
        await post_collection.insert_one(n_dict)
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"craete","subject":"post","object":n_dict})
        raise HTTPException(status_code=status.HTTP_200_OK,detail="inserted")
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)

@router.post("/post/edite")
async def edite(post:Post.Post_complet,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        old_item=await post_collection.find_one({"_id":ObjectId(post.id)})
        
        post_d=post.dict()
        if "prev_id" in post_d:
            post_d["prev_id"].append(post_d["id"])
        else:
            post_d.update({"prev_id":[post_d["id"]]})
        del post_d["id"]

        try:
            post_d.update({"count_like":old_item["count_like"],"count_comment":old_item["count_comment"]})
        except:
            post_d.update({"count_like":0,"count_comment":0})

        await post_collection.delete_one({"_id":ObjectId(post.id)})

        now_shamsi=jdatetime.datetime.now()
        true_date_str=now_shamsi.strftime("%Y-%m-%d %H:%M")
        post_d["date"]=true_date_str

        post_d["create_at"]=datetime.datetime.utcnow()

        await post_collection.insert_one(post_d)
        old_item.update({"id":old_item["_id"]})
        del old_item["_id"]
        await post_edited_collection.insert_one(old_item)

        await log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"post_notife","subject":post.dict(),"object":old_item})
        raise HTTPException(status_code=status.HTTP_200_OK,detail="edited")

    else:
        # print("************************** bad **************************")
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)



@router.delete("/post/delete/{itemid}")
async def delete(itemid:str,Xtoken: str = Header(""),Ujtoken:str=Header("")):
    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username=user_info_token["username"]
    if Xtoken=="0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        id=ObjectId(itemid)
        old_item=await post_collection.find_one({"_id":id})
        post_collection.delete_one({"_id":id})
        post_collection.delete_many({"post_id":id})
        post_comment_collectiom.delete_many({"post_id":itemid})
        log_collection.insert_one({"user":user_info_token_username,"time":datetime.datetime.now(),"action":"delete","subject":"post","object":old_item})
        return HTTPException(detail="deleted",status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(detail="bad requst",status_code=status.HTTP_400_BAD_REQUEST)