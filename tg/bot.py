import telebot
from botconfig import TOKEN


class SenderBot:
    TOKEN = TOKEN

    def __init__(self):
        self.tgbot = telebot.TeleBot(token=TOKEN)

    def send_to_telegram(self, tg_user_id: int, message: str):
        try:
            self.tgbot.send_message(tg_user_id, message)
        except telebot.apihelper.ApiTelegramException:
            print("Error 400: chat not found")


# id = int(input())
# b = SenderBot()
# for _ in range(5):
#     b.send_to_telegram(id, "test message")
