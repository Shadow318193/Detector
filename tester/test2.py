import requests
from bs4 import BeautifulSoup
from tester.interface import AvailableParser


class CheckHostParser(AvailableParser):
    def get_data(self, urls: list) -> list:
        data_out = []
        methods = {"ru3.node.check-host.net": "RU request",
                  "de4.node.check-host.net": "DE request",
                  "nl1.node.check-host.net": "NL request",
                  "us1.node.check-host.net": "USA request"}
        for url in urls:
            csrf_token = BeautifulSoup(requests.get(f"https://check-host.net/check-ping?host={url}").text,
                                       "html.parser").findAll("input")[1]["value"]

            token = BeautifulSoup(requests.get(f"https://check-host.net/check-ping?host={url}&csrf_token={csrf_token}"
                                               ).text, "html.parser").find("div", id="report_permalink").\
                find("a")["href"].split("/")[-1]
            param_tuples = [("slaves[]", "ru3.node.check-host.net"),
                            ("slaves[]", "de4.node.check-host.net"),
                            ("slaves[]", "nl1.node.check-host.net"),
                            ("slaves[]", "us1.node.check-host.net")]
            while True:
                data = requests.get(f"https://check-host.net/check_result/{token}", data=param_tuples).json()
                if set(data.keys()) == set(x[1] for x in param_tuples):
                    break
            for key, value in data.items():
                method = methods[key]
                success = True if value[0][0][0] == "OK" else False
                duration = int(value[0][0][1] * 1000)
                code = 200 if success else 404
                data_out.append({
                            "url": url,
                            "method": method,
                            "success": success,
                            "duration": duration,
                            "code": code
                })
        return data_out

    def __repr__(self):
        return "AvailableTester"


# if __name__ == "__main__":
#     x = CheckHostParser()
#     x1 = x.get_data(["proton.mskobr.ru"])
#     for i in x1:
#         print(i)
