import os
from typing import List, Literal

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..models.users import User
from ..utils.auth import get_current_user
from ..utils.response import success_response


router = APIRouter(prefix="/api/ai", tags=["ai"])


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str | None = None


@router.post("/chat")
async def chat(req: ChatRequest, user: User = Depends(get_current_user)):
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=500, detail="AI服务未配置，请联系管理员")

    endpoint = os.getenv(
        "AI_API_ENDPOINT",
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    ).strip()
    model = (req.model or os.getenv("AI_MODEL", "qwen3-max-preview")).strip()

    payload = {
        "model": model,
        "messages": [m.model_dump() for m in req.messages],
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                endpoint,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json=payload,
            )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"AI服务请求失败: {exc}") from exc

    if resp.status_code >= 400:
        try:
            err = resp.json()
            detail = err.get("error", {}).get("message") or str(err)
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=502, detail=f"AI服务返回错误: {detail}")

    body = resp.json()
    content = (
        body.get("choices", [{}])[0].get("message", {}).get("content")
        or body.get("output", {}).get("text")
        or ""
    )

    return success_response(message="AI回复成功", data={"content": content})
