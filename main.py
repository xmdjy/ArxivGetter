from utils import *

config=load_yaml('config.yaml')
sender=config['email']['sender']
server=config['email']['server']
port=config['email']['port']
password=config['email']['password']
to_addr=config['email']['to_addr']
query_content=config['papaers']['query_content']
max_results=config['papaers']['max_results']
tar=get_papers(query_content,max_results)
s=ai_summarize(tar)

def job():
    send_email(to_addr,s,port,server,sender,password)

if __name__ == "__main__":
    schedule.every().day.at("09:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)