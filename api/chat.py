import os
from fastapi import FastAPI, Body, HTTPException
import httpx
import json
from typing import Dict
import openai
import random
import uvicorn
from datetime import datetime

app = FastAPI()

openai.api_key = "your_openai_api_key"

chat_context_map = {}

prefix_prompt = "你是 燕千云101号数字化员工，是基于 GPT-3.5 接口的AI机器人，请认真、负责、详细的回答用户的问题，用心完成用户提出的任务并使用简体中文进行回答。"

def get_messages(user_msg: str, user_id: str, search_result: str):
    return [
        {
            "role": "system",
            "content": f"{prefix_prompt}\n你可以使用以下互联网信息辅助回答用户问题\n{search_result}\nCurrent date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        },
        *(chat_context_map[user_id] if user_id in chat_context_map else []),
        {
            "role": "user",
            "content": user_msg
        }
    ]

async def get_search(text: str):
    if not text:
        return ""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://duckduckgo-api.vercel.app/search?max_results=4&q={text}")
            data = response.json()
            search_prompt = f"Web search results:\n\n{data}\n\nMake sure to cite results using markdown url ref \"[[number](URL)]\" notation after the reference. If the provided search results refer to multiple subjects with the same name, write separate answers for each subject."
        return search_prompt
    except Exception as e:
        print(f"Error fetching search results: {e}")
        return ""

async def get_completion(messages):
    try:
        completion = openai.Completion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.9,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.7
        )
        return completion
    except Exception as e:
        print(f"Error in get_completion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_completion_text(completion):
    return completion.choices[0].message["content"]

@app.post("/api/chat")
async def chat_handler(prompt: str = Body(...), user_id: str = Body(...), network: bool = Body(True)):
    try:
        search_result = await get_search(prompt) if network else ""
        messages = get_messages(prompt, user_id, search_result)

        if user_id not in chat_context_map:
            chat_context_map[user_id] = []

        completion = await get_completion(messages)
        text = get_completion_text(completion)

        chat_context_map[user_id].append({"role": "user", "content": prompt})
        chat_context_map[user_id].append({"role": "assistant", "content": text})

        return {"result": text, "detail": completion, "text": text, "duration": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "prompt": prompt}
    except Exception as e:
        print(f"Error in chat_handler: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if name == "main":
    uvicorn.run(app, host="0.0.0.0", port=8000)