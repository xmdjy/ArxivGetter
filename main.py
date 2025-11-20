from utils import *

config=load_yaml('config.yaml')
sender=config['email']['sender']
server=config['email']['server']
port=config['email']['port']
password=config['email']['password']
to_addr=config['email']['to_addr']
query_content=config['papaers']['query_content']
max_results=config['papaers']['max_results']
paper_list=tar=get_papers(query_content,max_results)


def job():
    all_contents=[]
    for p in paper_list:
        res=ai_summarize(p)
        all_contents.append(res)
        time.sleep(1)
    email_body = "\n\n---\n\n".join(all_contents)
    day=date.today()
    email_header=f"您好,请查收{day}的论文推送,祝您愉快!"
    final_content = email_header + "\n\n" + email_body
    send_email(to_addr,final_content,port,server,sender,password)

if __name__ == "__main__":
    schedule.every().day.at("14:15").do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)