import telebot
import smtplib
from botconfig import TOKEN, POST_PASSWORD


class SenderBot:
    TOKEN = TOKEN
    POST_ADDRESS = "detector.esteam@gmail.com"
    POST_PASSWORD = POST_PASSWORD

    def __init__(self) -> None:
        self.tgbot = telebot.TeleBot(token=self.TOKEN)
        self.smtpbot = smtplib.SMTP('smtp.gmail.com', 587)
        self.smtpbot.starttls()

    def send_to_telegram(self, tg_user_id: int, message: str) -> None:
        try:
            self.tgbot.send_message(tg_user_id, message)
        except telebot.apihelper.ApiTelegramException:
            print("Error 400: chat not found")

    def send_to_mail(self, user_post_address: str, message: str) -> None:
        try:
            self.smtpbot.login(self.POST_ADDRESS, self.POST_PASSWORD)
            self.smtpbot.sendmail(self.POST_ADDRESS, user_post_address, message)
        except:
            print("Error")

# b = SenderBot()
# b.send_to_mail("test@gmail", "privet")
