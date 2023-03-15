import requests
from bs4 import BeautifulSoup
import json
from tester.interface import RatingParser


class UchebaParser(RatingParser):
    def get_data(self, ids: list):
        data = []
        for id_v in ids:
            html = requests.get(f"https://www.ucheba.ru/uz/{str(id_v[0])}").text
            soup = BeautifulSoup(html, "html.parser")
            json_data = json.loads(soup.find("script", type="application/ld+json").text)
            rate = json_data.get("aggregateRating", {"ratingValue": None})["ratingValue"]
            data.append({
                "site_id": id_v[1],
                "rating": rate,
            }
            )
        return data

    @staticmethod
    def search(execute: str):
        html = requests.get(f"https://www.ucheba.ru/json/search/suggestion?"
                     f"q={execute}").json()
        data = [[x["id"].split(":")[1], x["optiontext"]] for x in html["list"]]
        return data

if __name__ == "__main__":
    # obj = UchebaParser()
    # x = obj.get_data([('1153', 3), ('5723', 2)])
    print(UchebaParser.search("МФТИ"))