import pandas as pd
import numpy as np

# split_csv
split_csv = pd.read_csv("ChainMedic.annotates.csv")

df_variants = split_csv[
    ["variant", "var_description_zh", "biomark_group", "var_description", "var_link"]
]
# variant重复，去除
df_variants = df_variants.drop_duplicates(subset="variant", keep="first")
df_variants.to_csv("variants.csv", index=False)

##################################################


def process_drug_data(df):
    # 定义一个函数来拆分药物名称
    def split_drugs(row):
        if pd.isna(row["drug"]) or pd.isna(row["drug_zh"]):
            return [(np.nan, np.nan, np.nan)]

        drugs = row["drug"].split(",")
        drug_zhs = row["drug_zh"].split("，")
        drug_codes = row["drugncode"].split(",")
        return list(zip(drugs, drug_zhs, drug_codes))

    # 应用函数并展开结果
    split_data = df.apply(lambda row: split_drugs(row), axis=1).tolist()

    out = []
    for i in split_data:
        for j in i:
            out.append(j)

    # 创建新的 DataFrame
    # print(out)
    new_df = pd.DataFrame(out, columns=["drug", "drug_zh", "drugncode"])

    return new_df


df_drugs = split_csv[["drug", "drug_zh", "drugncode"]]
split_df = process_drug_data(df_drugs)
split_df = split_df.apply(pd.Series.explode)
split_df = split_df.drop_duplicates(subset="drugncode", keep="first")
split_df = split_df.dropna()  # 删除空行
split_df.to_csv("drugs.csv", index=False)

##################################################

df_cancers = split_csv[["cancercode", "cancertype", "cancertype_zh"]]
df_cancers = df_cancers.drop_duplicates(subset="cancertype", keep="first")
# cancertypw为空的行删除
df_cancers = df_cancers[df_cancers["cancertype_zh"].notna()]
# df_cancers = df_cancers.dropna()
df_cancers.to_csv("cancers.csv", index=False)

##################################################
df_treatments = split_csv[
    [
        "level",
        "treatment_info",
        "treatment_info_zh",
        "approved_info",
        "approval[0]",
        "guideline[0]",
        "drugncode",
        "cancertype",
        "variant",
    ]
]

# 删除level 为空时的空行
df_treatments = df_treatments[df_treatments["level"].notna()]
df_treatments = df_treatments.drop_duplicates(
    subset=["drugncode", "cancertype", "variant", "level"], keep="first"
)
# )
# df_treatments_A = df_treatments.drop_duplicates(
#     subset=[
#         "drugncode",
#         "cancercode",
#         "variant",
#     ],
#     keep="first",
# )

# diff = pd.merge(
#     df_treatments_A,
#     df_treatments_B,
#     on=["drugncode", "cancercode", "variant", "treatment_info"],
#     how="outer",
#     indicator=True,
# )

# # 选择只在 df_treatments_A 或只在 df_treatments_B 中的行
# diff_only_in_A = diff[diff._merge == "left_only"]
# diff_only_in_B = diff[diff._merge == "right_only"]

# print("Rows only in df_treatments_A:")
# print(diff_only_in_A)

# print("\nRows only in df_treatments_B:")
# print(diff_only_in_B)


# 改名approval[0]	guideline[0]
df_treatments.rename(
    columns={"approval[0]": "approval", "guideline[0]": "guideline"}, inplace=True
)
df_treatments.to_csv("treatments.csv", index=False)
# biomark = models.ForeignKey(
#     Biomark,on_delete=models.PROTECT, related_name="treatments"
# )
# drug = models.ManyToManyField(Drug,on_delete=models.PROTECT, related_name='treatments')
# cancer = models.ForeignKey(
#     Cancer, on_delete=models.PROTECT, related_name="treatments"
# )
