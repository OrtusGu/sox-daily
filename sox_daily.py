import akshare as ak
import requests
import json
import os
from datetime import datetime

# 从环境变量读取 Webhook URL
WECHAT_WEBHOOK = os.getenv("WECHAT_WEBHOOK")

def get_sox_data():
    """获取费城半导体指数最新数据"""
    try:
        df = ak.macro_global_sox_index()
        if df is None or len(df) == 0:
            print("数据为空，可能接口无返回")
            return None
        latest = df.iloc[-1]
        return {
            'date': latest['日期'],
            'value': latest['最新值'],
            'change': latest['涨跌幅'],  # 单位是 %
            'trend': "📈 上涨" if latest['涨跌幅'] > 0 else "📉 下跌"
        }
    except Exception as e:
        print(f"数据获取失败: {e}")
        return None

def send_to_wechat(data):
    """通过企业微信机器人推送消息"""
    if data is None:
        print("数据为空，跳过推送")
        return
    if not WECHAT_WEBHOOK:
        print("WECHAT_WEBHOOK 环境变量未设置")
        return

    # 构造 Markdown 消息内容
    content = f"""
### 📊 费城半导体指数 (SOX) 日报
**日期**: {data['date']}
**最新值**: {data['value']:.2f}
**涨跌幅**: {data['change']:.2f}% {data['trend']}
---
> 数据来源：东方财富
> 推送时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

    # 构造企业微信要求的 JSON 结构
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }

    # 将字典转换为 JSON 字符串，并处理中文
    json_str = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(WECHAT_WEBHOOK, data=json_str, headers=headers)
        print(f"企业微信返回: {response.text}")
        if response.status_code == 200:
            result = response.json()
            if result.get('errcode') == 0:
                print("✅ 推送成功")
            else:
                print(f"❌ 企业微信返回错误: {result}")
        else:
            print(f"❌ HTTP 错误: {response.status_code}")
    except Exception as e:
        print(f"请求发送异常: {e}")

if __name__ == "__main__":
    print("开始获取 SOX 数据...")
    data = get_sox_data()
    send_to_wechat(data)
    print("脚本执行结束")
