import requests
from pprint import pprint
from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os


class oncokb:

    def __init__(self):
        self.headers = {
            'Accept':
            'application/json',
            'Accept-Encoding':
            'gzip, deflate, br',
            'Accept-Language':
            'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Content-Type':
            'application/json',
            'Sec-Ch-Ua':
            '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
            'Sec-Ch-Ua-Mobile':
            '?0',
            'Sec-Ch-Ua-Platform':
            '"Windows"',
            'Sec-Fetch-Dest':
            'empty',
            'Sec-Fetch-Mode':
            'cors',
            'Sec-Fetch-Site':
            'same-origin',
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51'
        }

    def get_authorization(self):
        authorization_header = None

        def handle_request(request):
            nonlocal authorization_header
            headers = request.request.headers
            if 'authorization' in headers:
                authorization_header = headers['authorization']
            request.continue_()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.route('**/*', handle_request)
            page.goto('https://www.oncokb.org/gene/EGFR#tab=Biological')

            while not authorization_header:
                time.sleep(0.1)  # 等待 authorization_header 被设置
            browser.close()
        return {'Authorization': authorization_header}

    def get_response(self, url):
        response = requests.get(url, headers=self.headers)
        lisvar = response.json()
        if type(lisvar) != dict or lisvar.get('status') != 401:
            return lisvar
        self.headers.update(self.get_authorization())
        response = requests.get(url, headers=self.headers)
        return response.json()

    def gene_vars(self, gene: str) -> list:
        url = 'https://www.oncokb.org/api/private/search/variants/biological?hugoSymbol={}'.format(
            gene)
        lisvar = self.get_response(url)
        out = []
        for x in lisvar:
            #print(x)
            out.append({
                'varinat':
                gene + ' ' + x['variant']['alteration'],
                'var_Description':
                str(x['mutationEffectDescription']).replace(
                    '[[gene]]', 'gene'),
                'var_link':
                'https://www.oncokb.org/gene/{}/{}'.format(
                    gene, x['variant']['alteration'].replace(' ', '%20'))
            })
        return out

    def var_medics(self, varlink: str) -> list:
        url_p1 = varlink.split('/')[-2]
        url_p2 = varlink.split('/')[-1]
        url = 'https://www.oncokb.org/api/private/utils/variantAnnotation?hugoSymbol={}&referenceGenome=GRCh37&alteration={}'.format(
            url_p1, url_p2)
        out = []
        try:
            vars = self.get_response(url)['treatments']
            for var in vars:
                biomark_group = '/'.join(var['alterations'])
                drug = ','.join([x['drugName'] for x in var['drugs']])
                level = var['level']
                CancerType = var['levelAssociatedCancerType']['mainType'][
                    'name']
                approved_info = '\n'.join(var['approvedIndications'])
                treatment_info = var['description']
                out.append({
                    'biomark_group': biomark_group,
                    'drug': drug,
                    'level': level,
                    'CancerType': CancerType,
                    'approved_info': approved_info,
                    'treatment_info': treatment_info
                })
        except Exception as e:
            print('获取地址{}时异常 {}'.format(varlink, e))
            with open("tmp.txt", "w") as file:
                file.write('获取地址{}时异常 {}'.format(varlink, e))
        finally:
            return out if len(out) != 0 else [{
                'biomark_group': None,
                'drug': None,
                'level': None,
                'CancerType': None,
                'approved_info': None,
                'treatment_info': None
            }]

    def gene_all(self, gene):
        res = pd.DataFrame(self.gene_vars(gene))
        if res.empty:
            return res
        res['varinfos'] = res['var_link'].apply(self.var_medics)
        res = res.explode('varinfos')
        res = pd.concat(
            [res.drop('varinfos', axis=1), res['varinfos'].apply(pd.Series)],
            axis=1)
        return res

    def get_genelist(self):
        response = requests.get(
            "https://www.oncokb.org/api/v1/utils/cancerGeneList.txt")
        with open("cancerGeneList.txt", "wb") as file:
            file.write(response.content)


a = oncokb()

# Check if the file already exists in the current directory
if not os.path.isfile("cancerGeneList.txt"):
    a.get_genelist()
    print("基因列表文件下载成功")

Genelist = pd.read_csv('cancerGeneList.txt', sep='\t')['Hugo Symbol'].to_list()
for gene in Genelist:
    print(gene)
    if not os.path.exists('results/{}.xlsx'.format(gene)):
        varanno = a.gene_all(gene)
        varanno.to_excel('results/{}.xlsx'.format(gene))

###----------后面为对所有基因合并----------------###


def read_and_merge_excel_files(folder_path):
    excel_files = []

    # 获取文件夹下的所有文件
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            excel_files.append(file_name)
    dfs = []
    # 逐个读取Excel文件
    for excel_file in excel_files:
        file_path = os.path.join(folder_path, excel_file)
        df = pd.read_excel(file_path)
        dfs.append(df)
    # 合并数据框
    merged_df = pd.concat(dfs, ignore_index=True).drop("Unnamed: 0", axis=1)
    return merged_df


# 指定文件夹路径
folder_path = './results/'
# 调用函数读取并合并Excel文件
merged_df = read_and_merge_excel_files(folder_path)
# 打印合并后的数据
print(merged_df)
merged_df.to_excel('all.xlsx', index=None)

other = merged_df[merged_df['varinat'].str.contains(
    'Overexpression|Deletion|deletion|Mutations|Wildtyp|Amplification|Fusion|Duplication|>|splice|Promoter|trunc|Silencing|Hypermethylation|domain|fusion'
)]

snv = merged_df[~merged_df['varinat'].str.contains(
    'Overexpression|Deletion|deletion|Mutations|Wildtyp|Amplification|Fusion|Duplication|>|splice|Promoter|trunc|Silencing|Hypermethylation|domain|fusion'
)]
with pd.ExcelWriter('oncokb.xlsx') as writer:
    snv.to_excel(writer, sheet_name='pvar', index=False)
    other.to_excel(writer, sheet_name='other', index=False)