from flask import Flask, request

app = Flask(__name__)


@app.route('/search', methods=['GET', 'POST'])
def hello_world():  # put application's code here
    from duckduckgo_search import ddg

    if request.method == 'POST':
        keywords = request.form.get('q')
        max_results = int(request.form.get('max_results') or "3")
    else:
        keywords = request.args.get('q')
        max_results = int(request.args.get('max_results') or "3")

    
    results = ddg(keywords, region='wt-wt', max_results=max_results)
    print(results)
    return results


if __name__ == '__main__':
    app.run(host='0.0.0.0')
