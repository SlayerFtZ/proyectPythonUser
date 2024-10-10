from flask import Flask
from flask_mail import Mail
from flasgger import Swagger 
from controller.userController import registerRoutes
from controller.profileController import profileRoutes
from connection.database import * 
import signal
import sys

app = Flask(__name__)

swagger = Swagger(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mapache34lopez@gmail.com'
app.config['MAIL_PASSWORD'] = 'cmjykumibscmlzrs'

mail = Mail(app)


registerRoutes(app)
profileRoutes(app)


def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


if __name__ == '__main__':
    app.run(debug=True, threaded=False)
