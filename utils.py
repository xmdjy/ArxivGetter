import smtplib
from email.mime.text import MIMEText
from email.header import Header
import schedule
import time
from datetime import datetime,date
from zoneinfo import ZoneInfo
# from google import genai
import arxiv
import yaml
from yaml import safe_load
import os
from zai import ZhipuAiClient
import markdown

def send_email(to_addr,content,port,server,sender,password):
    day=date.today()
    html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
    subject=f"update arxiv papers falls on {day}"
    port=port
    server=server
    sender=sender
    password=password
    msg=MIMEText(html_content,'html','utf-8')
    msg['From']=Header(sender)
    msg['To']=Header(to_addr)
    msg['Subject']=Header(subject)
    server = smtplib.SMTP(server,port)
    server.starttls()  
    server.login(sender,password)
    server.sendmail(sender,[to_addr],msg.as_string())
    server.quit()

def ai_summarize(content):
    config=load_yaml('config.yaml')
    client = ZhipuAiClient(api_key=config['llm']['api_keys'])
    response = client.chat.completions.create(
        model="glm-4.5",
        messages=[
            {"role":"system","content":"你是专门研究计算机相关领域的专家，并且具有强大的文献阅读和总结能力。"},
            {"role":"user","content":f'请结合接下来给出的内容和要求帮我总结论文:\n内容：{content}\n说明和要求：给定的内容中每行代表一篇论文，前后用空格分开，前面是论文标题，后面是论文链接，请你阅读并分析总结给出的所有论文，然后对于每一篇论文生成摘要部分的中文翻译和关于文章创新点的400字中文总结，在回复论文总结之前加一句"您好,接下来是今天的推送,请查收"'}
        ],
        thinking={
            "type": "enabled",    # 启用深度思考模式
        },
        max_tokens=4096,          # 最大输出 tokens
        temperature=0.6           # 控制输出的随机性
    )
    return response.choices[0].message.content

def get_papers(query_content,max_results):
    tar=''
    search=arxiv.Search(
        query=query_content,
        max_results=max_results,
        sort_by = arxiv.SortCriterion.SubmittedDate, 
        sort_order = arxiv.SortOrder.Descending     
    )
    for res in search.results():
        tmp_res=f'{res.title} {res.entry_id}\n'
        tar+=tmp_res
    return tar

def load_yaml(config_path):
    with open(config_path,'r') as f:
        file=safe_load(f)
    return file