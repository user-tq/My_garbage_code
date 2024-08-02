import requests
import pandas as pd
from datetime import datetime


class DAAN:

    def __init__(self, user="谭强", password="123456"):
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        }
        self.user = user
        self.password = password

    @staticmethod
    def GNV(data, keys, rt="/"):
        """
        get_nested_value
        从嵌套的 JSON 数据中提取值。

        Args:
            data (dict): 嵌套的 JSON 数据。
            keys (list): 键或者列表的索引，分别必须为str和int。

        Returns:
            Any: 提取的值，如果未找到则返回 None。
        """
        current_data = data
        for key in keys:
            if (
                isinstance(key, str)
                and isinstance(current_data, dict)
                and key in current_data.keys()
            ) or (
                isinstance(key, int)
                and isinstance(current_data, list)
                and len(current_data) > key
            ):
                current_data = current_data[key]
            else:
                return rt
        return current_data or rt  # 为空亦'/'

    def re_authorization(self):
        data = {"UserName": "谭强", "Password": "123456"}  # 账号密码
        response = requests.post(
            "http://192.168.26.66:4007/v1/auth/login", headers=self.headers, json=data
        )
        if response.status_code == 200:
            self.headers.update(
                {
                    "Authorization": "Bearer {}".format(
                        response.json()["data"]["access_token"]
                    )
                }
            )
            return True
        else:

            raise Exception("登录失败")

    def get_task_status(self, task_id):

        url = "http://192.168.26.66:4007/v1/Analysis/GetAnalysisFlowStatusLog?id={}".format(
            task_id
        )
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            self.re_authorization()
        response = requests.get(url, headers=self.headers)
        data = response.json()["data"]["list"]

        result = {
            item["flowStatusName"]: item["operationTime"]
            for item in data
            if item["flowStatusName"] in ["分析完成", "任务排队"]
        }
        return result

    def get_simple_task_df(
        self,
        run_status=[81],
        time_start="2024-07-01 00:00:00",
        time_end="2024-08-01 00:00:00",
    ) -> pd.DataFrame:
        """
        81为运行完成
        """
        time_start = datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S")
        time_end = datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S")
        url = "http://192.168.26.66:4007/v1/Analysis/AnalysisTaskList"  # 你的URL
        data = {
            "current": 1,
            "pageSize": 500,
            "analysisListType": 0,
            "keyword": "",
            "qcStatus": [],
            "runStatus": run_status,
            "analysisQcStatus": [],
        }

        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code != 200:
            self.re_authorization()
        response = requests.post(url, headers=self.headers, json=data)
        data = response.json()["data"]["list"]
        x = pd.DataFrame(data)

        x["受检者名称"] = x["taskSampleList"].apply(lambda x: x[0]["personName"])
        x["癌种"] = x["taskSampleList"].apply(lambda x: x[0]["cancerTypeName"])
        x["样本id"] = x["analysisSampleQcList"].apply(lambda x: x[0]["sampleNo"])
        x = x[
            [
                "受检者名称",
                "癌种",
                "样本id",
                "chipNo",
                "analysisTaskId",
                "analysisTaskNo",
            ]
        ]

        filtered_rows = []
        for index, row in x.iterrows():
            task_status = self.get_task_status(row["analysisTaskId"])

            completion_time = datetime.strptime(
                task_status["分析完成"], "%Y-%m-%d %H:%M:%S"
            )
            if time_start <= completion_time <= time_end:
                row["任务排队"] = task_status["任务排队"]
                row["分析完成"] = task_status["分析完成"]
                filtered_rows.append(row)
        filtered_df = pd.DataFrame(filtered_rows)

        return filtered_df

    def get_one_task_df_SJZP(self, task_id, glist=[]):
        # 请求 URL
        url = "http://192.168.26.66:4007/v1/AnalysisDecode/ReadResultList"

        # 请求体数据
        data = {
            "resultList": [],
            "reportTypeList": [],
            "mutLevelList": [],
            "recommendMutLevelList": [],
            "mutationSourceList": [],
            "mutSummaryList": [],
            "impactList": [],
            "geneTypeList": [],
            "total": 0,
            "currenPage": 1,
            "pageSize": 500,
            "current": 1,
            "size": "small",
            "pageSizeOptions": ["20", "50", "100", "500"],
            "showSizeChanger": True,
            "showQuickJumper": True,
            "showLessItems": True,
            "analysisTaskId": task_id,
            "diseaseId": 154,
            "geneList": glist,
        }

        # 发送 POST 请求
        response = requests.post(url, json=data, headers=self.headers)
        if response.status_code != 200:
            self.re_authorization()
        response = requests.post(url, json=data, headers=self.headers)
        # 获取响应内容
        # print(response.status_code)
        # print(response.json())
        # with open("{}_out.json".format(task_id), 'w') as json_file:
        #     json.dump(response.json(), json_file)
        jsondata = response.json()
        excel_data = []
        # Chr	Start	End	Ref	Alt	Gene	Type	Transcript	cHGVS	pHGVS（简写）	pHGVS	VAF (%)
        for i in range(len(jsondata["data"]["list"])):

            len_hgvs = (
                0
                if jsondata["data"]["list"][i].get("hgvs") == None
                else len(jsondata["data"]["list"][i].get("hgvs"))
            )
            # print(len_hgvs)
            try:
                sh = jsondata["data"]["list"][i].get("reportSummary").get("reportType")
            except:
                sh = None
            try:
                vaf = (
                    float(jsondata["data"]["list"][i]["testResult"].get("standard_AF"))
                    * 100
                )
            except:
                vaf = 0
            tmp_dict = {
                "审核": sh,
                "Chr": self.GNV(
                    jsondata, ["data", "list", i, "location", "GRCh37", "chr"]
                ),
                "Start": self.GNV(
                    jsondata, ["data", "list", i, "location", "GRCh37", "pos1"]
                ),
                "End": self.GNV(
                    jsondata, ["data", "list", i, "location", "GRCh37", "pos2"]
                ),
                "Ref": jsondata["data"]["list"][i]["location"]["GRCh37"].get("ref"),
                "Alt": jsondata["data"]["list"][i]["location"]["GRCh37"].get("alt"),
                "Gene": (
                    jsondata["data"]["list"][i]["hgvs"][0]["gene"]
                    if len_hgvs != 0
                    else None
                ),
                "Type": jsondata["data"]["list"][i]["mutType"],
                "Transcript": (
                    jsondata["data"]["list"][i]["hgvs"][0]["trans"]
                    if len_hgvs != 0
                    else None
                ),
                "cHGVS": (
                    jsondata["data"]["list"][i]["hgvs"][0]["c_point"]
                    if len_hgvs != 0
                    else None
                ),
                "pHGVS（简写）": (
                    jsondata["data"]["list"][i]["hgvs"][0].get("p_point_short")
                    if len_hgvs != 0
                    else None
                ),
                "pHGVS": (
                    jsondata["data"]["list"][i]["hgvs"][0].get("p_point")
                    if len_hgvs != 0
                    else None
                ),
                "VAF(%)": vaf,
                "总深度": jsondata["data"]["list"][i]["testResult"].get("standard_DP"),
                "突变reads": jsondata["data"]["list"][i]["testResult"].get(
                    "standard_AD"
                ),
            }
            excel_data.append(tmp_dict)

        df = pd.DataFrame(excel_data)
        # df.to_excel("{}_output.xlsx".format(task_id),index=False)
        df["任务url"] = "http://192.168.26.66:4008/results?analysisTaskId={}".format(
            task_id
        )
        return df

    def get_task_df_with_gene(
        self,
        time_start: str = "2024-07-01 00:00:00",
        time_end: str = "2024-08-01 00:00:00",
        genes=[
            "AKT1",
            "ALK",
            "BRAF",
            "EGFR",
            "ERBB2",
            "KRAS",
            "MAP2K1",
            "MET",
            "NTRK1",
            "NTRK2",
            "NTRK3",
            "PIK3CA",
            "PTEN",
            "RET",
            "ROS1",
            "STK11",
            "TP53",
        ],
    ):
        task = self.get_simple_task_df(time_start=time_start, time_end=time_end)
        for gene in genes:
            task[gene] = 0

        for index, row in task.iterrows():
            # 通过task_id获取基因突变情况
            variants = self.get_one_task_df_SJZP(row["analysisTaskId"], glist=genes)
            variants = variants[
                (variants["审核"] == "推荐") | (variants["审核"] == "自填")
            ]
            print(variants)
            # 对variants按照基因统计数量，汇总到task中
            for gene in genes:
                task.at[index, gene] = variants[variants["Gene"] == gene].shape[0]

        return task


d = DAAN()
# task = d.get_task_list()
# task.to_csv("task.csv", index=False)
# s = d.get_simple_task_df()
# s.to_csv("simple_task.csv", index=False)
s = d.get_task_df_with_gene()
print(s)
s.to_csv("task_with_var_summary.csv", index=False)

# s = d.get_one_task_df_SJZP("4118")
# print(s)
