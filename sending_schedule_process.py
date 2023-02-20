import schedule
import time
from sending.bot import SenderBot


# db = DB("db", "detector2.db")
# db.global_init()
# print("generate_ok")

# schedule.every(30).seconds.do(tester.push_data, db=db)

while True:
    schedule.run_pending()
    time.sleep(1)
