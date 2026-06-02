from fastapi import Header, HTTPException, status, APIRouter, Depends
from bson import ObjectId
import datetime
import jwt
import jdatetime

from Model import Notife
from core.database import get_db

SECRET_KEY_USERNAME = "0041e6ad98c3ae252d"
ALGORITHM_USERNAME = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES_USERNAME = 5

router = APIRouter()


def get_collections(db):
    return (
        db.post_tag,
        db.notife,
        db.form,
        db.post,
        db.Users,
        db.log
    )


def convert_mongo_to_json(item):
    if isinstance(item, dict):
        return {k: (str(v) if isinstance(v, ObjectId) else v) for k, v in item.items()}
    return item


def fixid(user):
    user["_id"] = str(user["_id"])
    return user


@router.get("/notif/index/{type_user}")
async def index(
    type_user: str = "0",
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    post_tag_collection, notife_collection, form_collection, post_collection, user_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        if type_user == "0":
            notifes = notife_collection.find({}).sort("_id", -1)
        else:
            notifes = notife_collection.find({"moavenat": type_user}).sort("_id", -1)

        notife_list = []
        async for notife in notifes:
            notife_list.append(fixid(notife))

        log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "index",
            "subject": "notife",
            "object": type_user
        })

        return notife_list

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/notif/detail/{itemid}")
async def detail(
    itemid: str,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    post_tag_collection, notife_collection, form_collection, post_collection, user_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        id = ObjectId(itemid)
        notifes = notife_collection.find({"_id": id})

        notifes_list = []
        async for notife in notifes:
            notifes_list.append(fixid(notife))

        log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "detail",
            "subject": "notife",
            "object": itemid
        })

        return notifes_list

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/notif/create")
async def create(
    notife: Notife.Notife_insert,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    post_tag_collection, notife_collection, form_collection, post_collection, user_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        n_dict = notife.dict()
        n_dict.update({"count_like": 0, "count_comment": 0})

        now_shamsi = jdatetime.datetime.now()
        n_dict["date"] = now_shamsi.strftime("%Y-%m-%d %H:%M")

        await notife_collection.insert_one(n_dict)

        log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "create",
            "subject": "notife",
            "object": notife.dict()
        })

        raise HTTPException(status_code=status.HTTP_200_OK, detail="inserted")

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/notif/edite")
async def edite(
    notife: Notife.Notife_complet,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    post_tag_collection, notife_collection, form_collection, post_collection, user_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        old_item = await notife_collection.find_one({"_id": ObjectId(notife.id)})

        notif_d = notife.dict()

        if "prev_id" in notif_d:
            notif_d["prev_id"].append(notif_d["id"])
        else:
            notif_d["prev_id"] = [notif_d["id"]]

        del notif_d["id"]

        try:
            notif_d.update({
                "count_like": old_item["count_like"],
                "count_comment": old_item["count_comment"]
            })
        except:
            notif_d.update({"count_like": 0, "count_comment": 0})

        await notife_collection.delete_one({"_id": ObjectId(notife.id)})

        notif_d["date"] = jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        await notife_collection.insert_one(notif_d)

        await log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "edit_notife",
            "subject": notife.dict(),
            "object": old_item
        })

        raise HTTPException(status_code=status.HTTP_200_OK, detail="edited")

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.delete("/notif/delete/{itemid}")
async def delete(
    itemid: str,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    post_tag_collection, notife_collection, form_collection, post_collection, user_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        id = ObjectId(itemid)

        old_item = await notife_collection.find_one({"_id": id})

        await notife_collection.delete_one({"_id": id})
        await notife_collection.delete_many({"post_id": id})
        await log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "delete",
            "subject": "notife",
            "object": old_item
        })

        return HTTPException(detail="deleted", status_code=status.HTTP_200_OK)

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)