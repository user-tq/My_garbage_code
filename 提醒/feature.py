import requests
import time as time_module
import akshare as ak
from datetime import datetime, timedelta, time

cache_date = None
tradedays = [
    "2024-01-02",
    "2024-01-03",
    "2024-01-04",
    "2024-01-05",
    "2024-01-08",
    "2024-01-09",
    "2024-01-10",
    "2024-01-11",
    "2024-01-12",
    "2024-01-15",
    "2024-01-16",
    "2024-01-17",
    "2024-01-18",
    "2024-01-19",
    "2024-01-22",
    "2024-01-23",
    "2024-01-24",
    "2024-01-25",
    "2024-01-26",
    "2024-01-29",
    "2024-01-30",
    "2024-01-31",
    "2024-02-01",
    "2024-02-02",
    "2024-02-05",
    "2024-02-06",
    "2024-02-07",
    "2024-02-08",
    "2024-02-19",
    "2024-02-20",
    "2024-02-21",
    "2024-02-22",
    "2024-02-23",
    "2024-02-26",
    "2024-02-27",
    "2024-02-28",
    "2024-02-29",
    "2024-03-01",
    "2024-03-04",
    "2024-03-05",
    "2024-03-06",
    "2024-03-07",
    "2024-03-08",
    "2024-03-11",
    "2024-03-12",
    "2024-03-13",
    "2024-03-14",
    "2024-03-15",
    "2024-03-18",
    "2024-03-19",
    "2024-03-20",
    "2024-03-21",
    "2024-03-22",
    "2024-03-25",
    "2024-03-26",
    "2024-03-27",
    "2024-03-28",
    "2024-03-29",
    "2024-04-01",
    "2024-04-02",
    "2024-04-03",
    "2024-04-08",
    "2024-04-09",
    "2024-04-10",
    "2024-04-11",
    "2024-04-12",
    "2024-04-15",
    "2024-04-16",
    "2024-04-17",
    "2024-04-18",
    "2024-04-19",
    "2024-04-22",
    "2024-04-23",
    "2024-04-24",
    "2024-04-25",
    "2024-04-26",
    "2024-04-29",
    "2024-04-30",
    "2024-05-06",
    "2024-05-07",
    "2024-05-08",
    "2024-05-09",
    "2024-05-10",
    "2024-05-13",
    "2024-05-14",
    "2024-05-15",
    "2024-05-16",
    "2024-05-17",
    "2024-05-20",
    "2024-05-21",
    "2024-05-22",
    "2024-05-23",
    "2024-05-24",
    "2024-05-27",
    "2024-05-28",
    "2024-05-29",
    "2024-05-30",
    "2024-05-31",
    "2024-06-03",
    "2024-06-04",
    "2024-06-05",
    "2024-06-06",
    "2024-06-07",
    "2024-06-11",
    "2024-06-12",
    "2024-06-13",
    "2024-06-14",
    "2024-06-17",
    "2024-06-18",
    "2024-06-19",
    "2024-06-20",
    "2024-06-21",
    "2024-06-24",
    "2024-06-25",
    "2024-06-26",
    "2024-06-27",
    "2024-06-28",
    "2024-07-01",
    "2024-07-02",
    "2024-07-03",
    "2024-07-04",
    "2024-07-05",
    "2024-07-08",
    "2024-07-09",
    "2024-07-10",
    "2024-07-11",
    "2024-07-12",
    "2024-07-15",
    "2024-07-16",
    "2024-07-17",
    "2024-07-18",
    "2024-07-19",
    "2024-07-22",
    "2024-07-23",
    "2024-07-24",
    "2024-07-25",
    "2024-07-26",
    "2024-07-29",
    "2024-07-30",
    "2024-07-31",
    "2024-08-01",
    "2024-08-02",
    "2024-08-05",
    "2024-08-06",
    "2024-08-07",
    "2024-08-08",
    "2024-08-09",
    "2024-08-12",
    "2024-08-13",
    "2024-08-14",
    "2024-08-15",
    "2024-08-16",
    "2024-08-19",
    "2024-08-20",
    "2024-08-21",
    "2024-08-22",
    "2024-08-23",
    "2024-08-26",
    "2024-08-27",
    "2024-08-28",
    "2024-08-29",
    "2024-08-30",
    "2024-09-02",
    "2024-09-03",
    "2024-09-04",
    "2024-09-05",
    "2024-09-06",
    "2024-09-09",
    "2024-09-10",
    "2024-09-11",
    "2024-09-12",
    "2024-09-13",
    "2024-09-18",
    "2024-09-19",
    "2024-09-20",
    "2024-09-23",
    "2024-09-24",
    "2024-09-25",
    "2024-09-26",
    "2024-09-27",
    "2024-09-30",
    "2024-10-08",
    "2024-10-09",
    "2024-10-10",
    "2024-10-11",
    "2024-10-14",
    "2024-10-15",
    "2024-10-16",
    "2024-10-17",
    "2024-10-18",
    "2024-10-21",
    "2024-10-22",
    "2024-10-23",
    "2024-10-24",
    "2024-10-25",
    "2024-10-28",
    "2024-10-29",
    "2024-10-30",
    "2024-10-31",
    "2024-11-01",
    "2024-11-04",
    "2024-11-05",
    "2024-11-06",
    "2024-11-07",
    "2024-11-08",
    "2024-11-11",
    "2024-11-12",
    "2024-11-13",
    "2024-11-14",
    "2024-11-15",
    "2024-11-18",
    "2024-11-19",
    "2024-11-20",
    "2024-11-21",
    "2024-11-22",
    "2024-11-25",
    "2024-11-26",
    "2024-11-27",
    "2024-11-28",
    "2024-11-29",
    "2024-12-02",
    "2024-12-03",
    "2024-12-04",
    "2024-12-05",
    "2024-12-06",
    "2024-12-09",
    "2024-12-10",
    "2024-12-11",
    "2024-12-12",
    "2024-12-13",
    "2024-12-16",
    "2024-12-17",
    "2024-12-18",
    "2024-12-19",
    "2024-12-20",
    "2024-12-23",
    "2024-12-24",
    "2024-12-25",
    "2024-12-26",
    "2024-12-27",
    "2024-12-30",
    "2024-12-31",
]


def get_trade_dates():
    print("获取交易日历")
    return ak.tool_trade_date_hist_sina()


def is_within_trading_hours():
    now = datetime.now().time()
    morning_start = time(9, 30)
    morning_end = time(11, 30)
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)

    if (morning_start <= now <= morning_end) or (
        afternoon_start <= now <= afternoon_end
    ):
        return True
    return False


def if_today_is_trade():

    today = str(datetime.today().date())
    # 检查缓存日期是否为今天
    if today in tradedays:
        return True
    else:
        if today.split("-")[0] == str(cache_date).split("-")[0]:  # 今年
            return False
        else:
            trade_date_hist_sina_df = get_trade_dates()

    if today in trade_date_hist_sina_df["trade_date"].values:
        return True
    else:
        return False


def get_USDCNH():  # 离岸美元人民币
    """
    离岸美元人民币日涨幅
    """
    url = "https://push2.eastmoney.com/api/qt/stock/get"

    # 请求参数
    params = {
        "invt": "2",
        "fltt": "1",
        "cb": "",
        "fields": "f58,f107,f57,f43,f59,f169,f170,f152,f46,f60,f19,f532,f39,f44,f45,f119,f120,f121,f122",
        "secid": "133.USDCNH",
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "wbp2u": "|0|0|0|web",
        "dect": "1",
        "_": "1729180093091",
    }

    # 发送GET请求
    response = requests.get(url, params=params)
    # print(response.json())
    return round(response.json()["data"]["f43"] / 10000, 4)


def get_HSTECH():
    """ """
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "invt": "2",
        "fltt": "1",
        "cb": "",
        "fields": "f58,f107,f57,f43,f59,f169,f170,f152,f46,f60,f44,f45,f171,f47,f86,f292",
        "secid": "124.HSTECH",
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "wbp2u": "|0|0|0|web",
        "dect": "1",
        "_": "1729184310153",
    }

    response = requests.get(url, params=params)
    # 判断是否是数字
    # print(response.json())
    is_number = isinstance(response.json()["data"]["f170"], (int, float))
    if is_number:
        return round(response.json()["data"]["f170"] / 100, 4)
    else:
        return 0


def _get_realtime_stock_price_radio_vol(secid: str):
    """
    secid 为东财接口id，目前已知
    沪深300:  1.000300
    全A股:  47.800000
    创业板:  0.399006
    返回最新价，涨跌幅，成交量，单位万亿
    """
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "secid": secid,
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f53,f57,f59",
        "klt": "101",
        "fqt": "1",
        "beg": "0",
        "end": "20500101",
        "smplmt": "460",
        "lmt": "1000000",
    }

    response = requests.get(url, params=params)

    # print(response.json())
    if response.status_code == 200:
        data_list = response.json().get("data").get("klines")
        (
            ratime,
            price,
            vol,
            radio,
        ) = data_list[
            -1
        ].split(",")

        return float(price), float(radio), round(float(vol) / 1000000000000, 2)
    else:
        print("Failed to retrieve data:", response.status_code)
        return None


def _get_hs300_qh():
    """
    返回json
    """
    # 目标 URL
    base_url = "https://api.jijinhao.com/sQuoteCenter/realTime.htm?code=JO_338503"
    # 自定义的 HTTP 头部信息
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "referer": "https://m.quheqihuo.com/",
        "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0",
    }

    # 获取当前的 Unix 时间戳
    timestamp = str(int(time_module.time() * 1000))

    # 构建完整的 URL
    url = f"{base_url}&_={timestamp}"

    # 发送 GET 请求
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    # hq_str = "沪深加权,0,3541.6,3833.0,3895.2,3606.2,0,0,349796.0,3.90904119E11,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2024-09-27,14:59:59,00,1,291.3999,8.227917,0.0,0.0,3648.6,120,2024-09-27,14:59:59,"
    response.text
    # 移除字符串中的 'var hq_str = ' 和最后的逗号
    hq_str = response.text.replace("var hq_str = ", "").rstrip(",")

    # 将字符串分割成列表
    str_array = hq_str.split(",")

    # 初始化一个字典来存储数据
    CurrentHqData = {}

    # 将字符串转换为浮点数并存储到字典中

    CurrentHqData["price"] = float(str_array[3])
    CurrentHqData["date"] = str_array[40]
    CurrentHqData["time"] = str_array[41]

    return CurrentHqData["price"]


def get_hs300_baise():
    hs300_price, hs300_updown, _ = _get_realtime_stock_price_radio_vol("1.000300")

    return round(hs300_price - _get_hs300_qh(), 2)


def get_hs300_price_with_vol():
    hs300_price, hs300_updown, vol = _get_realtime_stock_price_radio_vol("1.000300")
    return round(hs300_price, 2), vol


def get_cyb_price_with_vol():
    cyb_price, cyb_updown, vol = _get_realtime_stock_price_radio_vol("0.399006")
    return round(cyb_price, 2), vol


def get_CN10_ratio():
    # 171.CN10Y
    return _get_realtime_stock_price_radio_vol("1.511260")[1]


def get_all_vol():
    return _get_realtime_stock_price_radio_vol("47.800000")[2]


def _stock_get_hs300():
    url = "https://datacenter-web.eastmoney.com/api/data/v1/get?sortColumns=SECURITY_CODE&sortTypes=-1&pageSize=300&pageNumber=1&reportName=RPT_INDEX_TS_COMPONENT&columns=SECUCODE%2CSECURITY_CODE%2CSECURITY_NAME_ABBR&quoteColumns=f2%2Cf3&quoteType=0&filter=(TYPE%3D%221%22)"
    # 发送GET请求
    response = requests.get(url)

    data = response.json()["result"]["data"]

    # 将数据转换为需要的格式
    formatted_data = []
    for item in data:
        formatted_data.append(
            {
                "代码": item["SECURITY_CODE"],
                "代码(简)": item["SECUCODE"],
                "名称": item["SECURITY_NAME_ABBR"],
                "最新价": (
                    float(item["f2"])
                    if item["f2"] is not None and not isinstance(item["f2"], str)
                    else None
                ),
                "涨跌幅": (
                    float(item["f3"])
                    if item["f3"] is not None and not isinstance(item["f3"], str)
                    else None
                ),
            }
        )

    return formatted_data


def sum_hs300():
    data = _stock_get_hs300()

    bins = [-float("inf"), -5, 0, 5, float("inf")]
    labels = ["t5d", "d50", "u05", "t5u"]

    grouped_data = {label: 0 for label in labels}

    total_rise = 0
    total_fall = 0

    for item in data:
        if item["涨跌幅"] is None:
            continue

        if item["涨跌幅"] > 0:
            total_rise += 1
        elif item["涨跌幅"] < 0:
            total_fall += 1

        for i in range(len(bins) - 1):
            if bins[i] <= item["涨跌幅"] < bins[i + 1]:
                grouped_data[labels[i]] += 1

    result = {**grouped_data, "tdn": total_fall, "tup": total_rise}

    return result


# 示例用法
# print(sum_hs300())

if __name__ == "__main__":
    print(get_hs300_baise())
    print(get_USDCNH())
    print(get_HSTECH())
    print(get_all_vol())
    print(sum_hs300())
    print(get_CN10_ratio())
