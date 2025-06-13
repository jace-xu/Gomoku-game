# Please install OpenAI SDK first: `pip3 install openai`
#key:sk-3be5fd048318406f9e9bd47a376aea71
from openai import OpenAI
import json

# 读取JSON文件
def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"读取文件出错：{e}")
        return None

# 示例：假设文件路径为'your_data.json'
json_data = read_json_file('history.json')
#这个是身份验证，使用key访问api接口，创建客户端对象
client = OpenAI(api_key="sk-3be5fd048318406f9e9bd47a376aea71", base_url="https://api.deepseek.com")
#向网站发送请求
response = client.chat.completions.create(
    model="deepseek-chat", #这个是你选择的模型
    messages=[
        {"role": "system", "content": "你是一个专业的五子棋手，你需要解析以下JSON数据并作出相应的评论："},
        {"role": "user", "content": json.dumps(json_data, ensure_ascii=False)}  # 转为字符串传递
    ],

    stream=False
)

print(response.choices[0].message.content)
