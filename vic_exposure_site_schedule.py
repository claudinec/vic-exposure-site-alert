import schedule

def job():
    print('Job done!')

schedule.every(10).seconds.do(job)

while True:
    schedule.run_pending()