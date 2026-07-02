import akshare as ak
import requests
import os
from datetime import datetime

WECHAT_WEBHOOK = os.getenv("WECHAT_WEBHOOK")

def get_sox_data():
    try:
        df = ak.macro_global_sox_index()
        latest = df.iloc[-1]
        return {
            'date': latest['日期'],
            'value': latest['最新值'],
            'change': latest['涨跌幅'],
            'trend': "📈 上涨" if latest['涨跌幅'] > 0 else "📉 下跌"
        }
    except Exception as e:
        print(f"数据获取失败: {e}")
        return None

def send_to_wechat(data):
    if data is None or WECHAT_WEBHOOK is None:
        return
    content = f"""
### 📊 费城半导体指数 (SOX) 日报
**日期**: {data['date']}
**最新值**: {data['value']:.2f}
**涨跌幅**: {data['change']:.2f}% {data['trend']}
---
> 数据来源：东方财富
> 推送时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    payload = {
        "msgtype": "markdown",
        "markdown": {"content": content}
    }
    requests.post(WECHAT_WEBHOOK, json=payload)

if __name__ == "__main__":
    data = get_sox_data()
    send_to_wechat(data)
    print("✅ 推送完成")
