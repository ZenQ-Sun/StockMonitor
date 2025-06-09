from datetime import datetime

import yfinance as yf
import requests
import json
import time
import schedule
import os

maxPrice = 0
webhook_url = os.getenv("WEBHOOK")


def send_dingtalk_message(webhook, content, at_mobiles=None, is_at_all=False):
    """
    发送文本消息到钉钉群

    Args:
        webhook: 钉钉机器人的 Webhook 地址
        content: 消息内容
        at_mobiles: 需要@的手机号列表
        is_at_all: 是否@所有人
    """
    if at_mobiles is None:
        at_mobiles = []

    # 构建消息体
    message = {
        "msgtype": "text",
        "text": {
            "content": "fromNas:" + content
        },
        "at": {
            "atMobiles": at_mobiles,
            "isAtAll": is_at_all
        }
    }

    # 发送请求
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook, data=json.dumps(message), headers=headers)

    # 检查响应
    if response.status_code == 200:
        result = response.json()
        if result.get('errcode') == 0:
            print("消息发送成功")
        else:
            print(f"消息发送失败: {result.get('errmsg')}")
    else:
        print(f"请求失败: {response.status_code} {response.text}")

def query_from_yh():
    info = None
    try:
        info = yf.Ticker("SAP.DE").info
    except Exception as e:
        print("query error")
        print(e)
    return info

def update_price():
    now = datetime.now()
    current_hour = now.hour
    if current_hour < 15 or current_hour > 24:
        print(f"不在监控时间段，跳过执行(时间: {time.strftime('%Y-%m-%d %H:%M:%S')})")
        return
    global maxPrice
    info = query_from_yh()
    currentPrice = info["currentPrice"]
    print(f"当前价格: {currentPrice} (时间: {time.strftime('%Y-%m-%d %H:%M:%S')})")
    if currentPrice > maxPrice:
        maxPrice = currentPrice
        print(f"maxPrice已更新为: {maxPrice} (时间: {time.strftime('%Y-%m-%d %H:%M:%S')})")
    if maxPrice * 0.97 > currentPrice:
        send_dingtalk_message(webhook_url, f"从{maxPrice}回落3%，当前：{currentPrice}, 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        maxPrice = currentPrice

def job():
    info = query_from_yh()
    currentPrice = info["currentPrice"]
    send_dingtalk_message(webhook_url, f"当前价格: {currentPrice} (时间: {time.strftime('%Y-%m-%d %H:%M:%S')})")


if __name__ == "__main__":
    send_dingtalk_message(webhook_url, "测试发送")
    info = query_from_yh()
    currentPrice = info["currentPrice"]
    send_dingtalk_message(webhook_url, f"监控启动,当前价格{currentPrice}")
    schedule.every(15).minutes.do(update_price)
    schedule.every().day.at("16:00").do(job)

    try:
        while True:
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        print("程序已停止")