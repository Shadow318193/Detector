import requests


class AvailabilTester:
    urls_to_parse = {"USA": "https://uk.2ipx.com:8888",
                     "UK": "https://uk.2ipx.com:8888",
                     "DE": "https://de.2ipx.com:8888",
                     "NL": "https://nl.2ipx.com:8888",
                     "RU": "https://ru.2ipx.com:8888",
                     "SG": "https://sg.2ipx.com:8888",
                     }

    def get_data(self, url):
        data = []
        signature = requests.get("https://2ip.ru/site-availability/").text
        signature = signature.split("var services = [")[1].split("{")[1][:-6].\
        replace("\n", "").replace("\t", " ").replace("     ", "").\
        split("\'")[1].split("\'")[0].split("/?")[1]
        for country, link in self.urls_to_parse.items():
            html = requests.get(link + "/?" + signature + url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                              " AppleWebKit/537.36 (KHTML, like Gecko)"
                              " Chrome/109.0.0.0 Safari/537.36",
                "Origin": "https://2ip.ru",
                "Host": link.split("://")[1],
                "Connection": "keep-alive",
                "Referer": "https://2ip.ru/",
                }).json()
            data.append({
                "method": country + " request",
                "success": html["success"],
                "duration": html["duration"],
                "code": html.get("code", 404)
            })

        return data


# x = AvailabilTester()
# x1 = x.get_data("coin.protonmos.ru")
# for i in x1:
#     print(i)
