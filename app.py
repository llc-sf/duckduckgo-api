from flask import Flask, request, jsonify
from duckduckgo_search import ddg
from flask import Flask, request, jsonify
import requests
import dayjs
import openai
import os

app = Flask(__name__)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        keywords = request.args.get('q')
        max_results = int(request.args.get('max_results') or "3")
    elif request.method == 'POST':
        data = request.get_json()
        keywords = data.get('q')
        max_results = int(data.get('max_results') or "3")

    results = ddg(keywords, region='wt-wt', max_results=max_results)
    print(results)
    return jsonify(results)


# 配置 OpenAI
openai.api_key = "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"

def get_search_results(keywords, max_results=2):
    try:
        results = ddg(keywords, region='wt-wt', max_results=max_results)
        return jsonify(results)
    except Exception as e:
        print("Error fetching search results:", e)
        return []

@app.route("/api/search", methods=["POST"])
def process_request():
    data = request.get_json()
    user_id = data.get("userId")
    user_msg = data.get("animal") or data.get("prompt") or ""
    network = data.get("network")
    search_enabled = True  # Set to False to disable search

    # Fetch search results
    search_results = []
    if search_enabled and network is not False:
        search_results = get_search_results(user_msg)
    
    # Generate response with GPT-3.5-turbo
    # You can implement the 'get_completion' function with the same logic as in the original Node.js code
    
    response_text = "Your GPT-3.5-turbo generated response"  # Replace this with the response from 'get_completion'

    return jsonify({
        "result": response_text,
        "text": response_text,
        "prompt": user_msg,
        "uniqueId": data.get("uniqueId"),
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0')

