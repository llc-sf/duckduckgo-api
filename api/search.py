import os
import json
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import asyncio
from datetime import datetime

app = FastAPI()

OPENAI_API_KEY = 'your_openai_api_key'

class ChatRequest(BaseModel):
    userId: str
    prompt: str
    network: Optional[bool] = True
    uniqueId: Optional[str] = None

class ChatResponse(BaseModel):
    result: str
    text: str
    duration: int
    prompt: str
    uniqueId: Optional[str] = None

chat_context_map = {}

async def get_completion(messages, max_error_count=2):
    url = "https://api.openai.com/v1/engines/davinci-codex/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.9,
        "top_p": 1,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.7
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            return response.json()
    except Exception as e:
        if max_error_count > 0:
            await asyncio.sleep(1)
            return await get_completion(messages, max_error_count - 1)
        else:
            raise

def get_completion_text(completion):
    return completion["choices"][0]["message"]["content"]

@app.post("/api/search", response_model=ChatResponse)
async def chat_handler(request: ChatRequest):
    try:
        user_id = request.userId
        user_msg = request.prompt
        network = request.network

        if not user_msg:
            raise HTTPException(status_code=400, detail="Bad Request: prompt is empty")

        search_result = ""
        if network:
            pass  # implement search functionality here if needed

        messages = [
            {
                "role": "system",
                "content": f"Prefix prompt text...\nCurrent date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            },
            *chat_context_map.get(user_id, []),
            {
                "role": "user",
                "content": user_msg
            }
        ]

        completion = await get_completion(messages)
        text = get_completion_text(completion)

        if user_id:
            chat_context_map[user_id] = chat_context_map.get(user_id, []) + [{"role": "user", "content": user_msg}, {"role": "assistant", "content": text}]

        duration = (datetime.now() - datetime.now()).seconds
        return ChatResponse(result=text, text=text, duration=duration, prompt=user_msg, uniqueId=request.uniqueId)
    except Exception as e:
        print(f"Error in chat_handler: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
