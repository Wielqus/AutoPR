import os
import requests


class TrelloClient:
    BASE_URL = "https://api.trello.com/1"

    def __init__(self):
        self.api_key = os.environ["TRELLO_API_KEY"]
        self.token = os.environ["TRELLO_TOKEN"]

    def _auth_params(self) -> dict:
        return {"key": self.api_key, "token": self.token}

    def get_ai_cards(self, board_id: str) -> list[dict]:
        list_id = os.environ.get("TRELLO_LIST_ID")
        if list_id:
            url = f"{self.BASE_URL}/lists/{list_id}/cards"
        else:
            url = f"{self.BASE_URL}/boards/{board_id}/cards"
        params = {**self._auth_params(), "fields": "id,idShort,name,desc,url,labels,pos"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        cards = response.json()
        return [
            card for card in cards
            if any(label.get("name") == "AI" for label in card.get("labels", []))
        ]

    def get_card_comments(self, card_id: str) -> list[dict]:
        url = f"{self.BASE_URL}/cards/{card_id}/actions"
        params = {**self._auth_params(), "filter": "commentCard", "fields": "data,date,memberCreator"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def update_card_status(self, card_id: str, status: str) -> None:
        url = f"{self.BASE_URL}/cards/{card_id}/actions/comments"
        params = {**self._auth_params(), "text": status}
        response = requests.post(url, params=params)
        response.raise_for_status()

    def move_card_to_list(self, card_id: str, list_id: str) -> None:
        url = f"{self.BASE_URL}/cards/{card_id}"
        params = {**self._auth_params(), "idList": list_id}
        response = requests.put(url, params=params)
        response.raise_for_status()
