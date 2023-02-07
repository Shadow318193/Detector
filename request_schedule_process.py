import schedule
import time
from tester.test1 import AvailableTester

tester = AvailableTester()

schedule.every(30).seconds.do(tester.push_data, urls=["instagram.com",
                                                     "google.com"])

while True:
    schedule.run_pending()
    time.sleep(1)
