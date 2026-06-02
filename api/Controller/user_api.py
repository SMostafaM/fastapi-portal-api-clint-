from fastapi import Header, HTTPException, status, APIRouter, Depends, Request
from bson import ObjectId
import datetime
import jwt
from core.database import get_db
from Model import User

SECRET_KEY_USERNAME = "0041e6ad98c3ae252d"
ALGORITHM_USERNAME = "HS256"

router = APIRouter()





# ---------------- Collections helper ----------------
def get_collections(db):
    return (
        db.Users,
        db.active_session,
        db.log,
    )


def fixid(user):
    user["_id"] = str(user["_id"])
    return user


# ---------------- Routes ----------------

@router.get("/user/index")
async def index(
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    User_collection, active_collection, log_collection = get_collections(db)

    user_info = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    username = user_info["username"]

    if Xtoken != "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        raise HTTPException(status_code=400, detail="bad request")

    users_list = []
    async for user in User_collection.find({}):
        users_list.append(fixid(user))

    await log_collection.insert_one({
        "user": username,
        "time": datetime.datetime.now(),
        "action": "index",
        "subject": "user",
        "object": "all_user"
    })

    return users_list


@router.get("/user/detail/{itemid}")
async def detail(
    itemid: str,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    User_collection, active_collection, log_collection = get_collections(db)

    user_info = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    username = user_info["username"]

    if Xtoken != "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        raise HTTPException(status_code=400, detail="bad request")

    user = await User_collection.find_one({"_id": ObjectId(itemid)})
    if not user:
        raise HTTPException(status_code=404, detail="not found")

    await log_collection.insert_one({
        "user": username,
        "time": datetime.datetime.now(),
        "action": "detail",
        "subject": "user",
        "object": user["username"]
    })

    return fixid(user)


@router.get("/user/detail/username/{username}")
async def detail_by_username(
    username: str,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    User_collection, active_collection, log_collection = get_collections(db)

    user_info = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    admin_user = user_info["username"]

    if Xtoken != "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        raise HTTPException(status_code=400, detail="bad request")

    user = await User_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="not found")

    await log_collection.insert_one({
        "user": admin_user,
        "time": datetime.datetime.now(),
        "action": "detail",
        "subject": "user",
        "object": username
    })

    return fixid(user)


@router.post("/user/create")
async def create(
    user: User.User_plus,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    User_collection, active_collection, log_collection = get_collections(db)

    user_info = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    admin_user = user_info["username"]

    if Xtoken != "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        raise HTTPException(status_code=400, detail="bad request")

    exist = await User_collection.find_one({"username": user.username})
    if exist:
        raise HTTPException(status_code=409, detail="duplicate username")

    await User_collection.insert_one(user.dict())

    await log_collection.insert_one({
        "user": admin_user,
        "time": datetime.datetime.now(),
        "action": "create",
        "subject": "user",
        "object": user.dict()
    })

    return {"detail": "inserted"}


@router.post("/user/edite")
async def edit(
    user: User.User_plus_complte,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    User_collection, active_collection, log_collection = get_collections(db)

    user_info = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    admin_user = user_info["username"]

    if Xtoken != "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        raise HTTPException(status_code=400, detail="bad request")

    old_user = await User_collection.find_one({"_id": ObjectId(user.id)})
    if not old_user:
        raise HTTPException(status_code=404, detail="not found")

    updated = False

    if user.password and user.password != old_user["password"]:
        old_user["password"] = user.password
        updated = True

    if user.type_user != old_user["type_user"]:
        old_user["type_user"] = user.type_user
        updated = True

    if user.name != old_user["name"]:
        old_user["name"] = user.name
        updated = True

    if user.img != "not_new_img":
        old_user["img"] = user.img
        updated = True

    if user.username != old_user["username"]:
        exist = await User_collection.count_documents({"username": user.username})
        if exist:
            raise HTTPException(status_code=409, detail="duplicate username")
        old_user["username"] = user.username
        updated = True

    if not updated:
        raise HTTPException(status_code=400, detail="bad request")

    await User_collection.delete_one({"_id": ObjectId(user.id)})
    await User_collection.insert_one(old_user)

    await log_collection.insert_one({
        "user": admin_user,
        "time": datetime.datetime.now(),
        "action": "edit_user",
        "subject": old_user["type_user"],
        "object": old_user["username"]
    })

    return {"detail": "edited"}


@router.delete("/user/delete/{itemid}")
async def delete(
    itemid: str,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    User_collection, active_collection, log_collection = get_collections(db)

    user_info = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    admin_user = user_info["username"]

    if Xtoken != "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":
        raise HTTPException(status_code=400, detail="bad request")

    old_user = await User_collection.find_one({"_id": ObjectId(itemid)})
    if not old_user:
        raise HTTPException(status_code=404, detail="not found")

    await User_collection.delete_one({"_id": ObjectId(itemid)})

    await log_collection.insert_one({
        "user": admin_user,
        "time": datetime.datetime.now(),
        "action": "delete",
        "subject": "user",
        "object": old_user
    })

    return {"detail": "deleted"}