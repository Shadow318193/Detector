import telebot
import smtplib
from botconfig import TOKEN, POST_ADDRESS


class SenderBot:
    TOKEN = TOKEN
    POST_ADDRESS = POST_ADDRESS

    def __init__(self) -> None:
        self.tgbot = telebot.TeleBot(token=TOKEN)
        self.smtpbot = smtplib.SMTP('smtp.gmail.com', 587)
        self.smtpbot.starttls()

    def send_to_telegram(self, tg_user_id: int, message: str) -> None:
        try:
            self.tgbot.send_message(tg_user_id, message)
        except telebot.apihelper.ApiTelegramException:
            print("Error 400: chat not found")

    def send_to_mail(self, user_post_address: str, message: str) -> None:
        try:
            self.smtpbot.login(POST_ADDRESS, 'P@ssw0rd')
            self.smtpbot.sendmail(POST_ADDRESS, user_post_address, message)
        except:
            print("Error")


# id = int(input())
# b = SenderBot()
# for _ in range(5):
#     b.send_to_telegram(id, "test message")
