import email
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import os
import time
import subprocess
import outlook_config

email_addr = outlook_config.email_addr
password = outlook_config.password

imp_server = outlook_config.imp_server
specialemail = outlook_config.specialemail
local_dir = outlook_config.local_dir

viewmail = outlook_config.viewmail


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
    print("邮件发送成功")


def fetch_email(
    filter_range="UNSEEN", part="BODY[]", specialbody=specialemail
):  # 获取最新
    try:
        with imaplib.IMAP4_SSL(imp_server) as server:  # 登录服务器
            server.login(email_addr, password)
            server.select("INBOX")
            email_all = server.uid(
                "SEARCH", None, filter_range, '(FROM "' + specialbody + '")'
            )[1][0].split()
            # print('共有', len(email_all), '封未读邮件')
            if len(email_all) != 0:
                # 最新邮件
                index = email_all[len(email_all) - 1]
                content = server.uid("FETCH", index, part)[1][0][
                    1
                ]  # RFC822和BODY[]作用相同
                # 转为email.message对象
                msg = email.message_from_bytes(content)

                return msg, index
            else:
                return None, None
    except:
        print("邮件获取失败")
        return None, None


def text_extract_oss(msg) -> str:
    try:
        content = msg.get_payload(decode=True)
        content = content.decode("UTF-8")
        url = re.findall(r"tos://[\w/-]+", content)[0]
    except Exception as e:
        print("路径获取错误 {}".format(e))
        url = None
    finally:
        return url


def csv_extract_oss(msg) -> str:
    try:
        content = msg.get_payload(decode=True)
        # charset = guess_charset(msg)
        content = content.decode("UTF-8")
    except Exception as e:
        print("csv 获取错误 {} ".format(e))
        content = None
    finally:
        return content


# 邮件的Subject或者Email中包含的名字都是经过编码后的字符串，要正常显示就必须decode，将原始邮件转化为可读邮件
# 将邮件改为未读邮件，operation：'+FLAGS'/'-FLAGS'，flag：r'(\Deleted \Flagged \Seen)'
def change_flag(index, operation, flag):
    """
    change_flag(index,'+FLAGS', '\\Flagged') # 标记一下
    change_flag(index,'+FLAGS', '\\Seen') # 已读一下
    """
    with imaplib.IMAP4_SSL(imp_server) as server:  # 登录服务器
        server.login(email_addr, password)
        server.select("INBOX")
        server.uid("STORE", index, operation, flag)


def get_url_csv_str():
    uid, url, csv_str = None, None, None
    message, uid = fetch_email("UNSEEN", "BODY.PEEK[]")  # 获取最新信息与邮件id

    if message is None:  # 邮箱没有信息
        return None, None, None
    for part in message.walk():
        # try:
        #     print(part.get_payload(decode=True).decode("UTF-8"))
        # except Exception as e:
        #     print('错误 {} '.format(e))
        # finally:
        #     print('---'*10)
        url2 = None
        if "text/plain" in part.get_content_type():
            url = text_extract_oss(part)
        if "text/html" in part.get_content_type():
            url2 = text_extract_oss(part)
        elif "text/csv" in part.get_content_type():
            csv_str = csv_extract_oss(part)
        url = text_extract_oss(part)
        url = url if url else url2
    return uid, url, csv_str


def get_cloud_files(cloud_path):  # 获取云上文件，到样本

    command = "tosutil.exe ls -d  {} ".format(cloud_path)
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print("ls error")

    return [x for x in stdout.decode("UTF-8").split("\n") if x.startswith("tos://")]
    # pass


def get_local_files(local_dir):  # 获取本地已有样本

    all_files_and_dirs = os.listdir(local_dir)

    # 过滤出所有的子目录
    subdirs = [
        name
        for name in all_files_and_dirs
        if os.path.isdir(os.path.join(local_dir, name))
    ]

    return subdirs


# def check_file_if_exist(cloud_sample_dir, local_sample_dir):
#     if os.
#     pass


def down_tos_1(cloudpath, local_store):
    local_dir = os.path.join(
        local_store, "-".join(cloudpath.split("/")[-1].split("-")[0:-3])
    )
    exist_samples = get_local_files(local_dir)

    cloud_files = get_cloud_files(cloudpath)
    # print("-" * 50)
    # print(exist_samples)
    # print(cloud_files)
    # print("-" * 50)
    erroInfo = []
    for url in cloud_files:
        if url.rstrip("/").split("/")[-1] not in exist_samples:
            # 下载
            command = "tosutil.exe cp {}  {}  -r ".format(url, local_dir)
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                erroInfo.append("{} 报错{}".format(url, stderr))
        else:
            print("本地已有该样本，重复")
            erroInfo.append("{} 已有该样本，重复".format(url))
    return erroInfo


def circle_print(total_time=0, str="无邮件或获取问题，等待"):
    list_circle = ["\\", "|", "/", "—"]
    for i in range(total_time * 4):
        time.sleep(0.25)
        print("\r{} {}".format(list_circle[i % 4], str), end="", flush=True)


if __name__ == "__main__":
    send_email("脚本启动", "邮件发送测试")
    while True:
        uid, url, csv_str = get_url_csv_str()
        if uid != None and url != None and csv_str != None:
            print("有数据，准备下载")
            print(uid)
            print(url)
            rt_erro = down_tos_1(url, local_dir)
            if rt_erro == None:
                send_email("下载完成", "{}已下载".format(url))
            else:
                print("下载出错或存在重复样本，建议排查")
                send_email(
                    "下载问题", "{}\n存在重复或下载问题".format("\n".join(rt_erro))
                )  # 发送邮件

            change_flag(uid, "+FLAGS", "\\Seen")  # 设为已读
            change_flag(uid, "+FLAGS", "\\Flagged")  # 标记一下
        elif uid != None:
            print("邮件无数据,标记为已读，等待")
            change_flag(uid, "+FLAGS", "\\Seen")
        else:
            # print('\r无邮件或获取问题，等待')
            # time.sleep(120)
            circle_print(total_time=120)
