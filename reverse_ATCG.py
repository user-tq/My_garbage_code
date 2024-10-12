import pandas as pd

# 创建一个字典来存储碱基的互补关系
complement = {
    "A": "T",
    "T": "A",
    "C": "G",
    "G": "C",
    "a": "t",
    "t": "a",
    "c": "g",
    "g": "c",
}


# 定义一个函数来获取反向互补序列
def reverse_complement(seq):
    return "".join(complement[base] for base in reversed(seq))


# 示例数据
# data = {"barcode1": ["ATGCGTAC", "CGTACGTA"], "barcode2": ["TGCATGCA", "GTACGTAC"]}

# # 创建DataFrame
# df = pd.DataFrame(data)

df = pd.read_csv("data.tsv", sep="\t")

# 生成反向互补序列
df["Barcode1_reverse_complement"] = df["Barcode1"].apply(reverse_complement)
df["Barcode2_reverse_complement"] = df["Barcode2"].apply(reverse_complement)

print(df)
df.to_csv("data_reverse_complement.xls", sep="\t", index=False)
