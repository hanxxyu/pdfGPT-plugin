from flask import Flask,request, Blueprint, send_from_directory, jsonify, make_response
from flask_cors import CORS
import functions.pdf as pdf
import json
import time 
import logging
# restful 跨域格式
#plugins = Blueprint("plugins", __name__)

# CORS 跨域

# 配置一个输出到控制台的处理器
app = logging.getLogger('app')
app.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('app.log')
app.addHandler(console_handler)
app.addHandler(file_handler)



plugins = Flask(__name__)
CORS(plugins, resources={r"/*": {"origins": "https://yiyan.baidu.com"}})

def make_json_response(data, status_code=200):
    response = make_response(json.dumps(data), status_code)
    response.headers["Content-Type"] = "application/json"
    return response

# def get_url_from_history(yiyan_info):
#     yiyan_info = json.loads(yiyan_info)
    
#     for ino in range(len(yiyan_info)): 
#         role = yiyan_info[ino]['role']
#         content = yiyan_info[ino]['content']
#         if role == 'user' and '<url>' in content:
#             substr = content.split('<url>')
#             url = substr[1].split('<url>')[0]
#     return url
def extract_info_from_request_body(request_body_json):
    # 解析 JSON 字符串
    yiyan_info = json.loads(request_body_json["yiyan_info"])
    query = request_body_json["query"]
    # 遍历列表中的每个项目
    for item in yiyan_info:
        # 检查角色和内容
        role = item['role']
        content = item['content']
        # 如果是用户角色并且内容中包含 URL
        if role == 'user' and '<url>' in content:
            # 提取 URL
            start_index = content.find('<url>') + len('<url>')
            end_index = content.find('</url>', start_index)
            url = content[start_index:end_index]
            break

    return url,query

@plugins.route("/pdf/load", methods=["POST"])
async def load_pdf():
        url = request.json.get('url',"")
        def event_stream():
        
            json_data1 = {"errCode": "0","actionName": "正在上传文件",
                          "actionContent": "上传文件完成",
                          "prompt":"上传文件成功，欢迎根据PDF进行提问"
                          }
            yield f"data:{json.dumps(json_data1, ensure_ascii=False)}\n\n"    

        return plugins.response_class(event_stream(), mimetype='text/event-stream')  

@plugins.route("/pdf/query", methods=["POST"])
async def query_pdf():
    # url = request.json.get('url',"")
    # query = request.json.get('query',"")
    # 提问不再需要上传url，要把以前的url链接在每次提问中提取出来：
    # query, yiyan_info_ori = request.json.get('yiyan_info', "")
    request_body = request.get_json()
    url,query = extract_info_from_request_body(request_body)
    logging.info(url)

    import requests
    response = requests.get(url)
    pdf_path= r"E:\GIT\pdfGPT-plugin\backend\corpus.pdf"
    with open(pdf_path,"wb") as file:
        file.write(response.content)
    pdf.load_recommender(pdf_path)
    answer = pdf.generate_answer(query)
    page_number = answer.split('no. ')[1].split(']')[0]
    answer_relavent = answer.split('"')[1]
    timestamp = str(time.time())
    def event_stream():
        json_data_result = {"answer": answer_relavent,
                            "page_id":page_number, 
                            "prompt": "任务：根据答案（answer）生成答案的大纲；输出：大纲为：（您的回答）+ [参引页面：page_id]，注意请传入pageid的实参不要直接输出page_id"}
        logging.info(answer)
        yield f"data:{json.dumps(json_data_result, ensure_ascii=False)}\n\n"
    return plugins.response_class(event_stream(), mimetype='text/event-stream')

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