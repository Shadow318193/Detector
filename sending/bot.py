import socket
import telebot
import smtplib
from email.message import EmailMessage
from .botconfig import TOKEN, POST_PASSWORD
from data.db_api import DB


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

    def send_to_email(self, dest_post_address: str, message_text: str) -> None:
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
        except smtplib.SMTPAuthenticationError:
            print("\033[31m{}".format("Authentication error."))
        except:
            print("\033[31m{}".format("Unknown error."))
        else:
            print("\033[32m{}".format(f"Successful sending to "
                                      f"{dest_post_address}"))

    def notify(self, db: DB) -> None:
        notification_data = db.notification()
        for ntf in notification_data:
            tg_id = ntf[0]
            email = ntf[1]
            site, site_url = ntf[2][0], ntf[2][1]
            prev_status_code, curr_status_code = ntf[3][0], ntf[3][1]
            prev_duration, curr_duration = ntf[4][0], ntf[4][1]
            if prev_status_code != curr_status_code:
                msg = f"Изменение в статус-коде сайта {site}\n" \
                      f"({site_url})\n" \
                      f"Предыдущий: {prev_status_code}\n" \
                      f"Текущий: {curr_status_code}\n" \
                      f"Предыдущее время ответа сайта: {prev_duration}\n" \
                      f"Текущее время ответа сайта: {curr_duration}"
                if email:
                    self.send_to_email(email, msg)
            else:
                msg = f"Изменение во времени ответа сайта {site}\n" \
                      f"({site_url})\n" \
                      f"Статус код: {prev_status_code}\n" \
                      f"Предыдущее время ответа сайта: {prev_duration}\n" \
                      f"Текущее время ответа сайта: {curr_duration}"
            if tg_id:
                self.send_to_telegram(tg_id, msg)


# if __name__ == "__main__":
#     b = SenderBot()
#     b.send_to_email("test@gmail.com", "tes_msg")
