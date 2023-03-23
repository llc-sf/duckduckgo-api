from flask import Flask, request, jsonify
from duckduckgo_search import ddg

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

if __name__ == '__main__':
    app.run(host='0.0.0.0')

