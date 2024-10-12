from mailer import Mailer
from mailer import Message
import threading
import asyncio
# import smtplib
# Initialize Mailer with the SMTP host and port
# lock = threading.Lock()
def send():
    #  with lock:
        sender = Mailer(host='smtp.gmail.com', port=587)

# Use TLS to secure the connection
        sender.use_tls = True

    # Login using email and password
        sender.login('exemple@gmail.com', 'password')
        message = Message(From="exemple@gmail.com",
                    To="exemple@gmail.com",
                    charset="utf-8")
        message.Subject = "Alert!!"
        message.Html = """There is <strong>Unknown Person</strong>! that has been detected"""
        message.Body = """This is alternate text."""

        sender.send(message)