from flask import Flask,request, Blueprint, send_from_directory, jsonify, make_response
from flask_cors import CORS
import functions.pdf as pdf
import json
# restful 跨域格式
#plugins = Blueprint("plugins", __name__)

# CORS 跨域

plugins = Flask(__name__)
CORS(plugins, resources={r"/*": {"origins": "https://yiyan.baidu.com"}})

def make_json_response(data, status_code=200):
    response = make_response(json.dumps(data), status_code)
    response.headers["Content-Type"] = "application/json"
    return response

@plugins.route("/pdf/load", methods=["POST"])
async def load_pdf():
        url = request.json.get('url',"")
        # pdf.download_pdf(url, 'corpus.pdf')
        print("url has been accepted")

        #下载url的pdf文件
        import requests
        response = requests.get(url)
        with open('corpus.pdf',"wb") as file:
            file.write(response.content)

        print("file has been downloaded")
        #先不加载pdf文件
        
        # pdf.load_recommender('corpus.pdf')
        results = "PDF has been downloaded"
        def event_stream():
        
            json_data1 = {"errCode": "0","actionName": "正在上传文件","actionContent": "上传文件完成"}
            yield f"data:{json.dumps(json_data1, ensure_ascii=False)}\n\n"    

        return plugins.response_class(event_stream(), mimetype='text/event-stream')  

@plugins.route("/pdf/query", methods=["POST"])
def query_pdf():
    try:
        data = request.get_json()
        question = data.get('query')
        url = data.get('url')
        if not question or not url:
            return jsonify({"error": "Question or URL not specified"}), 400
        pdf.download_pdf(url, 'corpus.pdf')
        pdf.load_recommender('corpus.pdf')
        answer = pdf.generate_answer(question)

        #to be finfished 
    

        return jsonify({"results": [answer]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@plugins.route('/.well-known/<path:path>', methods=['GET'])
def serve_file(path):
    return send_from_directory('static', path)

@plugins.route('/')
def index():
    return 'welcome to my webpage!'


@plugins.route('/<path:path>', methods=['GET'])
def serve_file2(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    plugins.run(debug=True, host='127.0.0.1',port=3333)