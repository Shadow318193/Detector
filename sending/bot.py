import socket
import telebot
import smtplib
from email.message import EmailMessage
from botconfig import TOKEN, POST_PASSWORD


class SenderBot:
    TOKEN = TOKEN
    POST_ADDRESS = "detector.esteam@yandex.ru"
    POST_PASSWORD = POST_PASSWORD

    def __init__(self) -> None:
        self.tgbot = telebot.TeleBot(token=self.TOKEN)

    def send_to_telegram(self, tg_user_id: int, message: str) -> None:
        try:
            self.tgbot.send_message(tg_user_id, message)
        except telebot.apihelper.ApiTelegramException:
            print("\033[31m{}".format("Error 400: chat not found."))

    def send_to_mail(self, dest_post_address: str, message_text: str) -> None:
        message = EmailMessage()
        message['Subject'] = 'Auto - report'
        message['From'] = self.POST_ADDRESS
        message['To'] = dest_post_address
        message.set_content(message_text)
        try:
            with smtplib.SMTP('smtp.yandex.ru', 587) as smtp_server:
                smtp_server.starttls()
                smtp_server.login(self.POST_ADDRESS, self.POST_PASSWORD)
                smtp_server.send_message(message)
        except socket.gaierror:
            print("\033[31m{}".format("No internet connection to send mail."))
        except TimeoutError:
            print("\033[31m{}".format("Timeout error."))
        except:
            print("\033[31m{}".format("Unknown error."))
        else:
            print("\033[32m{}".format(f"Successful sending to "
                                      f"{dest_post_address}"))


# if __name__ == "__main__":
#     b = SenderBot()
#     b.send_to_mail("test@yandex.ru", "test_message")
