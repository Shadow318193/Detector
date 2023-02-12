import schedule
import time
from tester.main_process import Parser
from data.db_api import DB

tester = Parser()
db = DB("db", "detector2.db")
db.global_init()
print("generate_ok")

schedule.every(20).seconds.do(tester.push_data, db=db)

while True:
    schedule.run_pending()
    time.sleep(1)
