import schedule
import time
from sending.bot import SenderBot


# schedule.every(30).seconds.do(tester.push_data, db=db)

while True:
    schedule.run_pending()
    time.sleep(1)
