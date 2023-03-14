import schedule
import time
from tester.main_process import Parser
from data.db_api import DB
from sending.bot import SenderBot

tester = Parser()
db = DB("db", "detector2.db")
db.global_init()
# print("generate_ok")
bot = SenderBot()

schedule.every(300).seconds.do(tester.push_data, db=db)
schedule.every(60).seconds.do(bot.notify, db=db)

while True:
    schedule.run_pending()
    time.sleep(1)
