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
        from_attributes=True  # 允许从ORM对象属性中取值 为什么要这么做?解答:因为在crud函数中我们是直接从数据库查询到User对象并返回的，而不是先将其转换为字典再传递给Pydantic模型。如果不设置from_attributes=True，Pydantic会默认只接受字典类型的数据输入，而无法直接从ORM对象的属性中取值，这样就会导致数据验证失败。因此，设置from_attributes=True允许Pydantic模型直接从ORM对象的属性中取值，使得我们可以直接使用数据库查询结果来创建响应数据模型，简化了代码并提高了效率。
    )

class UserAuthResponse(BaseModel):
    token:str
    user_info:UserInfoResponse = Field(...,alias="userInfo")
    model_config = ConfigDict(
        populate_by_name=True,# alias/字段名兼容
        from_attributes=True# 允许从ORM对象属性中取值
    )

class UserUpdateRequest(BaseModel):
    nickname:str = None
    avatar:str = None
    gender:str = None
    bio:str = None

class UseChangePasswordRequest(BaseModel):
    old_password:str = Field(...,alias="oldPassword",description="旧密码")
    new_password:str = Field(...,max_length=50,alias="newPassword",description="新密码")
