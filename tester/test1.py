import requests


class AvailableTester:
    urls_to_parse = {"USA": "https://uk.2ipx.com:8888",
                     "UK": "https://uk.2ipx.com:8888",
                     "DE": "https://de.2ipx.com:8888",
                     "NL": "https://nl.2ipx.com:8888",
                     "RU": "https://ru.2ipx.com:8888",
                     "SG": "https://sg.2ipx.com:8888",
                     }

    def get_data(self, urls: list) -> list:
        data = []
        for url in urls:
            cookies = {
                'dfjoCvIgkbblF5DJfa551AokP0o': 'igDggjMBG197PLliVZWgCW-B7R0',
                'LOW433wcIwWHRSdBwilP9srZ5Do': '1677254738',
                'w7uQRCdBmD7pu80CTALAL32VBhU': '1677341138',
                'G2tBy3ekpeZO3qeyhUTDLpkQWZ8': 'h4h2AJeROItN7NP3IXASSaddpG4',
                'PHPSESSID': 'go6m42natqlt0raf7lgn4rhdsn',
            }

            headers = {
                'authority': '2ip.ru',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'cache-control': 'max-age=0',
                # 'cookie': 'dfjoCvIgkbblF5DJfa551AokP0o=igDggjMBG197PLliVZWgCW-B7R0; LOW433wcIwWHRSdBwilP9srZ5Do=1677254738; w7uQRCdBmD7pu80CTALAL32VBhU=1677341138; G2tBy3ekpeZO3qeyhUTDLpkQWZ8=h4h2AJeROItN7NP3IXASSaddpG4; PHPSESSID=go6m42natqlt0raf7lgn4rhdsn',
                'referer': 'https://2ip.ru/site-availability/',
                'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            }

            signature = requests.get('https://2ip.ru/site-availability/',
                                    cookies=cookies, headers=headers).text
            signature = signature.split("var services = [")[1].split("{")[1][:-6]. \
                replace("\n", "").replace("\t", " ").replace("     ", ""). \
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
                    "url": url,
                    "method": country + " request",
                    "success": html["success"],
                    "duration": html["duration"],
                    "code": html.get("code", 404)
                })
        return data

    def __repr__(self):
        return "AvailableTester"


# x = AvailableTester()
# x1 = x.get_data(["google.com", "instagram.com"])
# for i in x1:
#     print(i)
