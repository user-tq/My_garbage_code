from feature import (
    get_hs300_price_with_vol,
    get_cyb_price_with_vol,
    if_today_is_trade,
    is_within_trading_hours,
)
import time
import sqlite3
from datetime import datetime
import threading
import tkinter as tk
import pandas as pd

import numpy as np


def init_db(table_name):
    conn = sqlite3.connect("stock.db")
    c = conn.cursor()
    # 动态创建表
    c.execute(
        f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            time TEXT,
            hs300price  REAL,
              hs300vol  REAL,
              cybprice  REAL,
              cybvol  REAL
        )
    """
    )
    conn.commit()
    conn.close()


def add_stock_data_to_db(times):
    while True:
        try:
            date_now = datetime.now().strftime("%Y-%m-%d")
            table_name = date_now.replace("-", "_")
            init_db(table_name)
            if if_today_is_trade() and is_within_trading_hours():

                time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                hs300price, hs300vol = get_hs300_price_with_vol()
                cybprice, cybvol = get_cyb_price_with_vol()

                conn = sqlite3.connect("stock.db")
                c = conn.cursor()
                c.execute(
                    f'INSERT INTO "{table_name}" (time,hs300price, hs300vol,cybprice,cybvol) VALUES (?,?,?,?,?)',
                    (time_now, hs300price, hs300vol, cybprice, cybvol),
                )
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(times)


def start_background_task(times=30):
    threading.Thread(target=add_stock_data_to_db, args=(times,), daemon=True).start()


def get_data_from_today():
    date_now = datetime.now().strftime("%Y-%m-%d")
    table_name = date_now.replace("-", "_")
    conn = sqlite3.connect("stock.db")
    df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
    conn.close()
    return df


def get_data_from_oneday(str):
    date_now = str
    table_name = date_now.replace("-", "_")
    conn = sqlite3.connect("stock.db")
    df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
    conn.close()
    return df


def get_kline(df, kmins):

    def volume_diff(group):
        # print(group)
        if len(group) < 2:
            # print(group)
            return 0
        return group.iloc[-1] - group.iloc[0]

    df["time"] = pd.to_datetime(df["time"])

    # 设置时间列为索引
    df.set_index("time", inplace=True)

    # 使用 resample 进行时间重采样，转换为 5 分钟 K 线数据
    ohlc_dict = {
        "cybprice": "ohlc",  # 获取开、高、低、收价
        "cybvol": volume_diff,  # 获取成交量c
    }

    # 进行重采样
    resampled_df = df.resample(str(kmins) + "min", label="right").apply(ohlc_dict)

    # 重命名列
    resampled_df.columns = ["open", "high", "low", "close", "volume"]

    # 打印结果
    return resampled_df


# Tkinter 主窗口
def main():
    root = tk.Tk()
    root.title("Stock Data Logger")

    label = tk.Label(root, text="后台任务正在运行...", padx=20, pady=20)
    label.pack()

    start_background_task(2)

    root.mainloop()


def sum_today_vwap():
    # data = get_data_from_today()
    data = get_data_from_oneday("2024-12-03")
    df = get_kline(data, 5)
    df = df[
        (df.index.time <= pd.to_datetime("11:30").time())
        | (df.index.time > pd.to_datetime("13:00").time())
    ]
    df["TP"] = (df["high"] + df["low"] + df["close"]) / 3
    # 最新行的vWAP

    df["vwap"] = (df["TP"] * df["volume"]).cumsum() / df["volume"].cumsum()
    df["cumcount"] = np.arange(
        1, len(df) + 1
    )  # 计算 (TP - vwap)^2 的累积和，除以累积的行数，并开平方根
    df["dev"] = np.sqrt(np.cumsum(np.power(df["TP"] - df["vwap"], 2)) / df["cumcount"])
    df["v1du"] = df["vwap"] + df["dev"]
    df["v1dd"] = df["vwap"] - df["dev"]
    df["v2du"] = df["vwap"] + 2 * df["dev"]
    df["v2dd"] = df["vwap"] - 2 * df["dev"]
    df["v3du"] = df["vwap"] + 3 * df["dev"]
    df["v3dd"] = df["vwap"] - 3 * df["dev"]

    # import pandas as pd

    # 假设 df 是你的原始数据框
    # 创建新的数据框
    new_df = pd.DataFrame(index=df.index)

    # 将买入信号的值放入新数据框
    buy_singles = {
        "cross1dd": "v1dd",
        "cross2dd": "v2dd",
        "cross3dd": "v3dd",
    }

    for b, v in buy_singles.items():
        df[b] = (df["low"].shift(1) < df[v].shift(1)) & (df["close"] > df[v])
        new_df[b] = df[b]

    # 将卖出信号的值放入新数据框
    sell_singles = {
        "cross2du": "v2du",
        "cross3du": "v3du",
    }

    for s, v in sell_singles.items():
        df[s] = (df["high"].shift(1) > df[v].shift(1)) & (df["close"] < df[v])
        new_df[s] = df[s]

    # 打印新数据框
    print(new_df)

    # print(df[])


if __name__ == "__main__":
    sum_today_vwap()

    # main()
