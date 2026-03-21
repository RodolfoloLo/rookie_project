from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..config.db_config import get_database
from ..schemas.users import UserRequest, UserAuthResponse, UserInfoResponse,UserUpdateRequest,UseChangePasswordRequest
from ..crud import users
from starlette import status
from ..utils.response import success_response
from ..utils.auth import get_current_user
from ..models.users import User

router = APIRouter(prefix="/api/user",tags=["users"])

@router.post("/register")
async def register(
        user_data:UserRequest,
        db:AsyncSession = Depends(get_database)
):
    existing_user = await users.get_user_by_username(db,user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="用户已存在")
    user = await users.create_user(db,user_data)
    token = await users.create_token(db,user.id)
    #封装通用成功响应模式
    response_data = UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功",data=response_data)

@router.post("/login")
async def login(
        user_data:UserRequest,
        db:AsyncSession = Depends(get_database)
):
    user = await users.authenticate_user(db,user_data.username,user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="用户名或密码错误")
    token= await users.create_token(db,user.id)
    response_data = UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登陆成功",data=response_data)

@router.get("/info")
async def get_user_info(
        user:User=Depends(get_current_user)
):
    return success_response(message="获取用户信息成功",data=UserInfoResponse.model_validate(user))

@router.put("/update")
async def update_user_info(
        user_data:UserUpdateRequest,
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_database)
):
    user = await users.update_user(db,user.username,user_data)
    return success_response(message="更新用户信息成功",data=UserInfoResponse.model_validate(user))

@router.put("/password")
async def update_password(
        password_data:UseChangePasswordRequest,
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_database)
):
    result = await users.change_password(db,user,password_data.old_password,password_data.new_password)
    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="修改密码失败,请稍后再试")
    return success_response(message="密码修改成功")
