import requests
from bs4 import BeautifulSoup
import json


class RatingParser:
    def get_data(self, ids: list):
        data = []
        for id_v in ids:
            html = requests.get(f"https://www.ucheba.ru/uz/{str(id_v)}").text
            soup = BeautifulSoup(html, "html.parser")
            json_data = json.loads(soup.find("script", type="application/ld+json").text)
            print(json_data["aggregateRating"])



if __name__ == "__main__":
    obj = RatingParser()
    obj.get_data([1153, 5723])