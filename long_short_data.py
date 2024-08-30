import requests
import pandas as pd
from datetime import datetime
import smtplib
import akshare as ak
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser

script_dir = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(script_dir, "config.ini"))


email_addr = config["email"]["address"]
password = config["email"]["password"]

imp_server = "outlook.office365.com"  # cmlabs.com.cn

viewmail = "tq17bio@qq.com"  # 监控下载进度邮箱


def connect_to_server():
    smtp_server = "smtp-mail.outlook.com"
    port = 587
    server = smtplib.SMTP(smtp_server, port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(email_addr, password)
    return server


def send_email(title, text):
    server = connect_to_server()
    sender_email = email_addr
    receiver_email = viewmail
    email = MIMEMultipart()
    email["From"] = sender_email
    email["To"] = receiver_email
    email["Subject"] = title
    email.attach(MIMEText(text, "plain"))
    server.send_message(email)
    server.quit()


import akshare as ak
import pandas as pd


def stock_get(code):
    """
    指数代码
    """

    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    A = stock_zh_a_spot_em_df

    index_stock_cons_csindex_df = ak.index_stock_cons_csindex(symbol=code)
    B = index_stock_cons_csindex_df

    filtered_A = A[A["代码"].isin(B["成分券代码"])]

    return filtered_A


def sum_my_format(symbol: str):

    symbol_map = {
        "沪深300": "000300",
        "中证1000": "000852",
    }

    data = stock_get(symbol_map[symbol])
    bins = [-float("inf"), -6, -3, 0, 3, 6, float("inf")]
    labels = ["跌停至-6%", "-6%至-3%", "-3%至0%", "0%至3%", "3%至6%", "6%至涨停"]
    # 统计每个分组的数量
    data["涨跌幅分组"] = pd.cut(data["涨跌幅"], bins=bins, labels=labels)

    # 统计每个分组的数量
    grouped_data = data["涨跌幅分组"].value_counts().sort_index()

    # 创建一个新的DataFrame来存储结果，并将分组作为列名
    result = pd.DataFrame(grouped_data).T
    result.columns = labels

    # 计算总涨数和总跌数
    total_rise = data[data["涨跌幅"] > 0].shape[0]
    total_fall = data[data["涨跌幅"] < 0].shape[0]

    # 增加总涨数和总跌数列
    result["总跌"] = total_fall
    result["总涨"] = total_rise

    result.index = [symbol]

    return result


def iftodyistrade():
    # 判断今天是否在 trade_date 列中

    tool_trade_date_hist_sina_df = ak.tool_trade_date_hist_sina()
    today = datetime.today().date()  # .strftime("%Y-%m-%d")
    if today in tool_trade_date_hist_sina_df["trade_date"].values:
        return True
    else:
        return False


def get_data(date: str, cs: str):
    """
    20240518
    IM  1000
    IF  300
    """
    data = requests.get(
        "https://qhhqzl.eastmoney.com/marketFutuWeb/dragonAndTigerInfo/getLongAndShortPosition?date={}&contract={}&market=220".format(
            date, cs
        )
    )
    # print(data.json()['data']['tradeDate'])
    df_data_1 = pd.DataFrame(data.json()["data"]["longInfoList"][:20])
    df_data_2 = pd.DataFrame(data.json()["data"]["shortInfoList"][:20])
    return {
        "数据日期": data.json()["data"]["tradeDate"],
        "看多增持": df_data_1["longChange"].sum(),
        "看空增持": df_data_2["shortChange"].sum(),
    }


def circle_print(total_time=0, str="时机未到，等待"):
    list_circle = ["\\", "|", "/", "—"]
    for i in range(total_time * 4):
        time.sleep(0.25)
        print("\r{} {}".format(list_circle[i % 4], str), end="", flush=True)


def job(tag):
    if iftodyistrade():

        A = sum_my_format("沪深300")
        B = sum_my_format("中证1000")
        ab = pd.concat([A, B])
        abhtml = ab.to_html()
        # sendstr = sendstr + abhtml
        # send_email(sendstr)
        now = datetime.now()
        formatted_date = now.strftime("%Y%m%d")
        ifdata = get_data(formatted_date, "IF")  # 沪深300
        imdata = get_data(formatted_date, "IM")  # 中证1000
        if ifdata["数据日期"] == formatted_date:  # 今日期货龙虎榜更新
            # send_email(
            qhstr = "{}情况".format(
                ifdata["数据日期"]
            ), "IF看多增持：{}  看空增持：{}\nIM看多增持：{}  看空增持：{}".format(
                ifdata["看多增持"],
                ifdata["看空增持"],
                imdata["看多增持"],
                imdata["看空增持"],
            )
        else:
            qhstr = ""
        send_email("{}_{}情况".format(formatted_date, tag), abhtml + "\n" + qhstr)


if __name__ == "__main__":
    # 获取当前日期
    import schedule
    import time
    import sys

    if len(sys.argv) - 1 != 0:
        job("测试")
    else:
        schedule.every().day.at("14:50").do(lambda: job("三点前"))
        schedule.every().day.at("17:30").do(lambda: job("三点后"))
        while True:
            # 运行所有可以运行的任务
            schedule.run_pending()
            # time.sleep(600)
            circle_print(1)
