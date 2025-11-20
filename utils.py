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

def ai_summarize(paper):
    title = paper.title
    authors = ", ".join([author.name for author in paper.authors])
    abstract = paper.summary
    primary_category = paper.primary_category
    config=load_yaml('config.yaml')
    client = ZhipuAiClient(api_key=config['llm']['api_keys'])
    prompt = f"""
# **角色**
你是一位顶尖的AI领域学术研究员，拥有博士学位，目前在世界一流大学担任教授。你非常擅长以一种清晰、结构化且专业的方式，向你的研究生介绍一篇最新的前沿论文。

# **任务**
我将为你提供一篇英文AI论文的标题、作者和摘要。请你仔细阅读并分析这些信息，然后为我生成一份详细的中文解读报告。

# **输出格式 (非常重要)**
请严格按照下面的 Markdown 格式生成你的报告，不要添加任何额外的开场白或结束语（例如，不要说“好的，这是您的报告”）。

```markdown
### 📝 论文解读：[论文标题]

**1. 核心关键词**
*   (提取3-5个最能代表论文内容的核心技术或领域关键词，用顿号分隔)

**2. 摘要汉化**
> (将提供的英文摘要流畅、准确地翻译成中文，保持段落结构。)

**3. 创新点与贡献 (深入解读)**
*   **核心思想**: (用一两句话，高度概括这篇论文最核心的、与众不同的思想或方法。)
*   **具体创新**:
    *   **创新点一**: (详细描述第一个关键创新，它解决了什么问题？是如何实现的？)
    *   **创新点二**: (详细描述第二个关键创新...)
    *   (如果还有，继续列出)
*   **价值与意义**: (简要说明这项研究可能带来的影响、应用前景或对领域的贡献。)"""

    response = client.chat.completions.create(
        model="glm-4.5",
        message={"role": "user", "content": prompt},
        thinking={
            "type": "enabled",    # 启用深度思考模式
        },
        max_tokens=1024,          # 最大输出 tokens
        temperature=0.6,
        top_p=0.9         
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
    return list(search.results())

def load_yaml(config_path):
    with open(config_path,'r') as f:
        file=safe_load(f)
    return file