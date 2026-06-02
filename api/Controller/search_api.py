from fastapi import FastAPI, Header, HTTPException, status, Depends
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
from core.database import get_db

# کلید مخفی برای ارسال نام کاربری در هدر درخواست ها
SECRET_KEY_USERNAME = "0041e6ad98c3ae252d"
ALGORITHM_USERNAME = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES_USERNAME = 5

# ایجاد یک router جدید
router = APIRouter()


def get_collections(db):
    return (
        db.post,
        db.notife,
        db.form_archive,
        db.log
    )


def convert_mongo_to_json(item):
    if isinstance(item, dict):
        return {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in item.items()}
    return item


def fixid(user):
    user["_id"] = str(user["_id"])
    return user


@router.get("/search/main")
async def index(
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    type_req: str = "all",
    data: str = "all",
    page: str = 1,
    db=Depends(get_db)
):
    post_collection, notife_collection, form_archive_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        page = int(page) - 1

        form_arch = form_archive_collection.find({
            "$or": [
                {"title": {"$regex": data, "$options": "i"}},
                {"text": {"$regex": data, "$options": "i"}}
            ]
        }).sort("_id", -1).skip(page * 10).limit(10)

        notifs = notife_collection.find({
            "$and": [
                {"show": True},
                {
                    "$or": [
                        {"title": {"$regex": data, "$options": "i"}},
                        {"text": {"$regex": data, "$options": "i"}}
                    ]
                }
            ]
        }).sort("_id", -1).skip(page * 10).limit(10)

        posts = post_collection.find({
            "$and": [
                {"show": True},
                {
                    "$or": [
                        {"title": {"$regex": data, "$options": "i"}},
                        {"text": {"$regex": data, "$options": "i"}}
                    ]
                }
            ]
        }).sort("_id", -1).skip(page * 10).limit(10)

        posts_list = []

        async for post in posts:
            post.update({"type_search": "آگهی"})
            posts_list.append(fixid(post))

        async for post in notifs:
            post.update({"type_search": "اطلاعیه"})
            posts_list.append(fixid(post))

        async for post in form_arch:
            post.update({"type_search": "فرم"})
            posts_list.append(fixid(post))

        log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "search",
            "subject": type_req,
            "object": data
        })

        return posts_list

    else:
        raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/search/count/main")
async def post_count(
    type_req: str = "notif",
    data: str = "all",
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    post_collection, notife_collection, form_archive_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        count_post_1 = await form_archive_collection.count_documents({
            "$or": [
                {"title": {"$regex": data, "$options": "i"}},
                {"text": {"$regex": data, "$options": "i"}}
            ]
        })

        count_post_2 = await notife_collection.count_documents({
            "$and": [
                {"show": True},
                {
                    "$or": [
                        {"title": {"$regex": data, "$options": "i"}},
                        {"text": {"$regex": data, "$options": "i"}}
                    ]
                }
            ]
        })

        count_post_3 = await post_collection.count_documents({
            "$and": [
                {"show": True},
                {
                    "$or": [
                        {"title": {"$regex": data, "$options": "i"}},
                        {"text": {"$regex": data, "$options": "i"}}
                    ]
                }
            ]
        })

        count_post = count_post_1 + count_post_2 + count_post_3

        log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "count_post",
            "subject": type_req,
            "object": data
        })

        return count_post

    else:
        raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/search")
async def index(
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    type_req: str = "all",
    data: str = "all",
    page: str = 1,
    db=Depends(get_db)
):
    post_collection, notife_collection, form_archive_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        if type_req == "notif":
            target_collection = notife_collection
        elif type_req == "post":
            target_collection = post_collection

        if type_req == "form_archive":
            page = int(page) - 1

            posts = form_archive_collection.find({
                "$or": [
                    {"title": {"$regex": data, "$options": "i"}},
                    {"text": {"$regex": data, "$options": "i"}}
                ]
            }).sort("_id", -1).skip(page * 10).limit(10)

        else:
            page = int(page) - 1

            posts = target_collection.find({
                "$and": [
                    {"show": True},
                    {
                        "$or": [
                            {"title": {"$regex": data, "$options": "i"}},
                            {"text": {"$regex": data, "$options": "i"}}
                        ]
                    }
                ]
            }).sort("_id", -1).skip(page * 10).limit(10)

        posts_list = []

        async for post in posts:
            posts_list.append(fixid(post))

        log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "search",
            "subject": type_req,
            "object": data
        })

        return posts_list

    else:
        raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/search/count")
async def post_count(
    type_req: str = "notif",
    data: str = "all",
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    post_collection, notife_collection, form_archive_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        if type_req == "notif":
            target_collection = notife_collection
        else:
            target_collection = post_collection

        if type_req == "form_archive":
            count_post = await form_archive_collection.count_documents({
                "$or": [
                    {"title": {"$regex": data, "$options": "i"}},
                    {"text": {"$regex": data, "$options": "i"}}
                ]
            })
        else:
            count_post = await target_collection.count_documents({
                "$and": [
                    {"show": True},
                    {
                        "$or": [
                            {"title": {"$regex": data, "$options": "i"}},
                            {"text": {"$regex": data, "$options": "i"}}
                        ]
                    }
                ]
            })

        log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "count_post",
            "subject": type_req,
            "object": data
        })

        return count_post

    else:
        raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)