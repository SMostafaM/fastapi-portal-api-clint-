from fastapi import FastAPI, Header, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import Notife
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import datetime
import jwt

from core.database import get_db


# کلید مخفی برای ارسال نام کاربری در هدر درخواست ها
SECRET_KEY_USERNAME = "0041e6ad98c3ae252d"
ALGORITHM_USERNAME = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES_USERNAME = 5


# ایجاد یک router جدید
router = APIRouter()


# ================== get_collections ==================
def get_collections(db):
    return (
        db.post_tag,
        db.notife,
        db.form,
        db.post,
        db.Users,
        db.log
    )


# ================== utils ==================
def convert_mongo_to_json(item):
    if isinstance(item, dict):
        return {
            key: (str(value) if isinstance(value, ObjectId) else value)
            for key, value in item.items()
        }
    return item


def fixid(user):
    user["_id"] = str(user["_id"])
    return user


# ================== ENDPOINTS ==================

@router.get("/index/moavenat/list")
async def index(
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):

    post_tag_collection, notife_collection, form_collection, post_collection, user_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        list_moavenat_coursor = user_collection.find({}, {"_id": 0, "type_user": 1})
        list_moavenat = await list_moavenat_coursor.to_list(length=None)

        l_mo = []
        for item in list_moavenat:
            l_mo.append(item["type_user"])

        l_mo = list(set(l_mo))
        l_mo.remove("0")

        try:
            l_mo.remove("100")
        except:
            pass

        try:
            l_mo.remove("90")
        except:
            pass

        await log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "index",
            "subject": "list",
            "object": "moavenat"
        })

        return l_mo

    else:
        raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/index/notif")
async def index(
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    moavenat: str = "all",
    important: bool = None,
    show: bool = None,
    page: int = 0,
    db=Depends(get_db)
):

    post_tag_collection, notife_collection, form_collection, post_collection, user_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        query = {}

        if moavenat != "all":
            query.update({"moavenat": str(moavenat)})
        if important is not None:
            query.update({"important": important})
        if show is not None:
            query.update({"show": show})

        if page == 0:
            notifes = notife_collection.find(query).sort("_id", -1)
        else:
            page = page - 1
            notifes = notife_collection.find(query).sort("_id", -1).skip(page * 10).limit(10)

        notife_list = []
        async for notife in notifes:
            notife_list.append(fixid(notife))

        await log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "index",
            "subject": "notife",
            "object": query
        })

        return notife_list

    else:
        raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/notif/count/{type_req}/{data}")
@router.get("/notif/count/{type_req}/")
async def post_count(
    type_req: str = "all",
    data: str = "all",
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):

    post_tag_collection, notife_collection, form_collection, post_collection, user_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        if type_req == "all":
            count_post = await notife_collection.count_documents({"show": True})
        else:
            if type_req == "important":
                if data == "True":
                    count_post = await notife_collection.count_documents({"show": True, type_req: True})
                else:
                    count_post = await notife_collection.count_documents({"show": True, type_req: False})
            else:
                count_post = await notife_collection.count_documents({"show": True, type_req: data})

        await log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "count_notif",
            "subject": type_req,
            "object": data
        })

        return count_post

    else:
        raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/index/form")
async def index_form(
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    type_form: str = "all",
    show: bool = None,
    page: str = "0",
    db=Depends(get_db)
):

    post_tag_collection, notife_collection, form_collection, post_collection, user_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        query = {}

        if type_form != "all":
            query.update({"type_form": str(type_form)})
        if show is not None:
            query.update({"show": show})

        if page == "0":
            forms = form_collection.find(query).sort("_id", -1)
        else:
            forms = form_collection.find(query).sort("_id", -1).skip(int(page) * 10).limit(10)

        forms_list = []
        async for form in forms:
            forms_list.append(fixid(form))

        await log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "index",
            "subject": "form",
            "object": query
        })

        return forms_list

    else:
        raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/index/tag")
async def index_tag(
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    type_form: str = "all",
    show: bool = None,
    db=Depends(get_db)
):

    post_tag_collection, notife_collection, form_collection, post_collection, user_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        forms = post_tag_collection.find({})

        forms_list = []
        async for form in forms:
            forms_list.append(form["tag"])

        await log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "index",
            "subject": "tag",
            "object": "all"
        })

        return forms_list

    else:
        raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)