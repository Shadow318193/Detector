import schedule
import time
from tester.test1 import AvailableTester

tester = AvailableTester()

schedule.every(15).seconds.do(tester.push_data, url="instagram.com")

while True:
    schedule.run_pending()
    time.sleep(1)