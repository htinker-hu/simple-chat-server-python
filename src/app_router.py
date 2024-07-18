import os
import logging
from fastapi import APIRouter
import requests
import json
from typing import List
from rest.chat_request import Message, ChatRequest
from rest.chat_response import ChatResponse


log = logging.getLogger("root.chat")

SYSTEM_MESSAGE = """你是一名资深的专业的猫科医生，你能够根据猫的症状，诊断出猫的疾病，并简短地给出治疗方案，不超过50字。"""

app = APIRouter(
    prefix="/chat",
    tags=["Chat Completions"]
)

def get_access_token():
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
    qianfan_ak = os.environ.get("QIANFAN_AK")
    qianfan_sk = os.environ.get("QIANFAN_SK")
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={qianfan_ak}&client_secret={qianfan_sk}"

    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")


def send(messages: List, access_token: str):
    url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token={access_token}"
    if(len(messages)>5):
        messages = messages[-5:]

    msgs = [msg.dict() for msg in messages]
    payload = json.dumps({
        "system": SYSTEM_MESSAGE,
        "messages": msgs
    })
    headers = {
        'Content-Type': 'application/json'
    }
    log.debug(f"Payload: {payload}")

    response = requests.request("POST", url, headers=headers, data=payload)

    data = response.json()
    log.debug(f"Response: {data}")
    return data["result"]


ACCESS_TOKEN = get_access_token()
log.info(f"Access Token: {ACCESS_TOKEN}")


@app.post("/completions")
async def completions(request: ChatRequest):
    log.info(f"Received request data: {request.json()}")
    if request.messages:
        result = send(request.messages, ACCESS_TOKEN)
        return ChatResponse.from_value(result)

    return ChatResponse.from_value("Yes, you are great")
