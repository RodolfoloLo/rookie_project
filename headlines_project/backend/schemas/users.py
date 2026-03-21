from pydantic import BaseModel,Field,ConfigDict
from typing import Optional

class UserRequest(BaseModel):
    username:str
    password:str

class UserInfoBase(BaseModel):
    """
    用户信息基础数据模型
    """
    nickname:Optional[str] = Field(None,max_length=50,description="昵称")
    avatar:Optional[str] = Field(None,max_length=255,description="头像URL")
    gender:Optional[str] = Field(None,max_length=10,description="性别")
    bio:Optional[str] = Field(None,max_length=500,description="个人简介")

class UserInfoResponse(UserInfoBase):
    id:int
    username:str
    model_config = ConfigDict(
        from_attributes=True  # 允许从ORM对象属性中取值
    )

class UserAuthResponse(BaseModel):
    token:str
    user_info:UserInfoResponse = Field(...,alias="userInfo")
    model_config = ConfigDict(
        populate_by_name=True,#alias/字段名兼容
        from_attributes=True#允许从ORM对象属性中取值
    )

class UserUpdateRequest(BaseModel):
    nickname:str = None
    avatar:str = None
    gender:str = None
    bio:str = None

class UseChangePasswordRequest(BaseModel):
    old_password:str = Field(...,alias="oldPassword",description="旧密码")
    new_password:str = Field(...,max_length=50,alias="newPassword",description="新密码")
