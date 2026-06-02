from fastapi import FastAPI, Header, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import Notife, Interaction
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


router = APIRouter()


# ================== GET COLLECTIONS ==================
def get_collections(db):
    return (
        db.Users,
        db.notife,
        db.post,
        db.like,
        db.notif_comment,
        db.post_comment,
        db.deleted_comment,
        db.log
    )


# ================== UTILS ==================
def convert_mongo_to_json(item):
    if isinstance(item, dict):
        return {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in item.items()}
    return item


def fixid(user):
    user["_id"] = str(user["_id"])
    return user


# ================== LIKE ==================
@router.post("/like/{type_like}/{count_like}")
async def like(
    type_like: str,
    count_like: str,
    like: Interaction.like_insert,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):

    User_collection, notife_collection, post_collection, like_collectiom, notif_comment_collectiom, post_comment_collectiom, deleted_comment_collectiom, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        like_di = like.dict()
        like_exist = await like_collectiom.find_one(like_di)
        bson_id = ObjectId(like.post_id)

        l_c = count_like

        # DISLIKE
        if like_exist is not None and type_like == "dislike":
            await like_collectiom.delete_one(like_di)

            await log_collection.insert_one({
                "user": user_info_token_username,
                "time": datetime.datetime.now(),
                "action": "like",
                "subject": "remove",
                "object": like_di
            })

            if like.type_post == "notif":
                notif = await notife_collection.find_one({"_id": bson_id})
                l_c = int(notif["count_like"]) - 1
                await notife_collection.update_one({"_id": bson_id}, {"$set": {"count_like": l_c}})

            elif like.type_post == "post":
                post = await post_collection.find_one({"_id": bson_id})
                l_c = int(post["count_like"]) - 1
                await post_collection.update_one({"_id": bson_id}, {"$set": {"count_like": l_c}})

        # LIKE
        elif like_exist is None and type_like == "like":
            now_shamsi = jdatetime.datetime.now()
            like_di["date"] = now_shamsi.strftime("%Y-%m-%d %H:%M")

            await like_collectiom.insert_one(like_di)

            await log_collection.insert_one({
                "user": user_info_token_username,
                "time": datetime.datetime.now(),
                "action": "like",
                "subject": "add",
                "object": like_di
            })

            if like.type_post == "notif":
                notif = await notife_collection.find_one({"_id": bson_id})
                l_c = int(notif["count_like"]) + 1
                await notife_collection.update_one({"_id": bson_id}, {"$set": {"count_like": l_c}})

            elif like.type_post == "post":
                post = await post_collection.find_one({"_id": bson_id})
                l_c = int(post["count_like"]) + 1
                await post_collection.update_one({"_id": bson_id}, {"$set": {"count_like": l_c}})

        return str(l_c)

    else:
        raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


# ================== COMMENT INSERT ==================
@router.post("/comment/insert")
async def comment_insert(
    comment: Interaction.comment,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):

    User_collection, notife_collection, post_collection, like_collectiom, notif_comment_collectiom, post_comment_collectiom, deleted_comment_collectiom, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        comment_di = comment.dict()
        comment_di["date"] = jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        bson_id = ObjectId(comment.post_id)

        await log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "comment_insert",
            "object": comment_di
        })

        if comment.type_post == "notif":
            await notif_comment_collectiom.insert_one(comment_di)
            notif = await notife_collection.find_one({"_id": bson_id})
            l_c = int(notif["count_comment"]) + 1
            await notife_collection.update_one({"_id": bson_id}, {"$set": {"count_comment": l_c}})

        elif comment.type_post == "post":
            await post_comment_collectiom.insert_one(comment_di)
            post = await post_collection.find_one({"_id": bson_id})
            l_c = int(post["count_comment"]) + 1
            await post_collection.update_one({"_id": bson_id}, {"$set": {"count_comment": l_c}})

        raise HTTPException(status_code=status.HTTP_200_OK, detail="inserted")

    else:
        raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


# ================== COMMENT GET ==================
@router.get("/comment/{post_id}/{type_post}/{user}/{self_id}")
async def comment(
    post_id: str,
    type_post: str,
    user: str = "all",
    self_id: str = "0",
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):

    User_collection, notife_collection, post_collection, like_collectiom, notif_comment_collectiom, post_comment_collectiom, deleted_comment_collectiom, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken != "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)

    final_list = []

    if type_post == "notif":
        comments = notif_comment_collectiom.find(
            {"$and": [{"user": {"$ne": self_id}}, {"post_id": post_id}]}
        ) if user == "all" else notif_comment_collectiom.find({"post_id": post_id, "user": user})

    elif type_post == "post":
        comments = post_comment_collectiom.find(
            {"$and": [{"user": {"$ne": self_id}}, {"post_id": post_id}]}
        ) if user == "all" else post_comment_collectiom.find({"post_id": post_id, "user": user})

    if user == "all":
        async for item in comments:
            u = await User_collection.find_one({"username": item["user"]})
            item["user_name"] = u["name"]
            item["user_img"] = u["img"]
            item["_id"] = str(item["_id"])
            final_list.append(item)
    else:
        async for item in comments:
            item["_id"] = str(item["_id"])
            u = await User_collection.find_one({"username": user_info_token_username})
            item["user_name"] = u["name"]
            item["user_img"] = u["img"]
            final_list.append(item)

    return final_list


# ================== DELETE COMMENT ==================
@router.delete("/comment/delete/{type_post}/{comment_id}")
async def delete(
    type_post: str,
    comment_id: str,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):

    User_collection, notife_collection, post_collection, like_collectiom, notif_comment_collectiom, post_comment_collectiom, deleted_comment_collectiom, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken != "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)

    bson_id = ObjectId(comment_id)

    if type_post == "notif":
        comment = await notif_comment_collectiom.find_one({"_id": bson_id})
    else:
        comment = await post_comment_collectiom.find_one({"_id": bson_id})

    bson_id_post = ObjectId(comment["post_id"])

    await log_collection.insert_one({
        "user": user_info_token_username,
        "time": datetime.datetime.now(),
        "action": "comment_delete",
        "object": comment
    })

    await deleted_comment_collectiom.insert_one(comment)

    if comment["type_post"] == "notif":
        notif = await notife_collection.find_one({"_id": bson_id_post})
        l_c = int(notif["count_comment"]) - 1
        await notife_collection.update_one({"_id": bson_id_post}, {"$set": {"count_comment": l_c}})
        await notif_comment_collectiom.delete_one({"_id": bson_id})

    elif comment["type_post"] == "post":
        post = await post_collection.find_one({"_id": bson_id_post})
        l_c = int(post["count_comment"]) - 1
        await post_collection.update_one({"_id": bson_id_post}, {"$set": {"count_comment": l_c}})
        await post_comment_collectiom.delete_one({"_id": bson_id})

    return HTTPException(detail="deleted", status_code=status.HTTP_200_OK)