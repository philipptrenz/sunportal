#!/usr/bin/python3
"""
"""

import smtplib, threading, time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

class Mail:

    def __init__(self, config, database):
        self.config = config
        self.db = database
        self.mail_config = self.config.get_mail_config()
        self.is_enabled = self.mail_config["enabled"]
        self.stop_threads = False
        self.sent_messages = dict()

    def start(self):
        self.timer_thread = threading.Thread(target=self.run) # run self.run every [interval] seconds
        self.timer_thread.start()
        self.config.log('mail: service started')

    def run(self):
        interval  = self.mail_config["check_interval"] # in seconds
        while not self.stop_threads:
            inverters = self.db.get_inverters()
            for inv in inverters:

                # if status is not okay
                if inv['status'] != 'OK' and self.do_send_mail('status', inv['serial']):
                    msg = 'Inverter \'%s\' [Serial: %s] has abnormal status: \'%s\'' % ( inv['name'], inv['serial'], inv['status'])
                    self.config.log('mail: sending error mail', msg)
                    message_id = '%s-%s-%s' % (datetime.now().timestamp(), inv['serial'], 'status')
                    self.send_mail('Abnormal inverter status', msg, message_id=message_id)
                    self.set_sent_mail('status', inv['serial'], message_id)
                elif inv['status'] == 'OK' and self.do_send_clear_mail('status', inv['serial']):
                    msg = 'Inverter \'%s\' [Serial: %s] status is now back to normal' % (inv['name'], inv['serial'])
                    self.config.log('mail: sending back to normal mail', msg)
                    message_id = self.get_message_id('status', inv['serial'])
                    self.send_mail('Abnormal inverter status', msg, message_id=message_id, in_reply_to=True)
                    self.set_sent_mail('status', inv['serial'], message_id, sent=False)

                # if last timestamp is older than 24h
                older_than_24h = datetime.fromtimestamp(inv['ts']) < (datetime.now() - timedelta(days=1))
                if  older_than_24h and self.do_send_mail('timeout', inv['serial']):
                    ts = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.fromtimestamp(inv['ts']))
                    msg = 'Last update from inverter \'%s\' [Serial: %s] is more than 24 hours ago, last timestamp: %s' % (
                    inv['name'], inv['serial'], ts)
                    self.config.log('mail: sending error mail', msg)
                    message_id = '%s-%s-%s' % (datetime.now().timestamp(), inv['serial'], 'timeout')
                    self.send_mail('Last inverter data older than 24h', msg, message_id=message_id)
                    self.set_sent_mail('timeout', inv['serial'],  message_id)
                elif not older_than_24h and self.do_send_clear_mail('timeout', inv['serial']):
                    ts = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.fromtimestamp(inv['ts']))
                    msg = 'Inverter \'%s\' [Serial: %s] now delivers values again, last timestamp: %s' % (inv['name'], inv['serial'], ts)
                    self.config.log('mail: sending back to normal mail', msg)
                    message_id = self.get_message_id('timeout', inv['serial'])
                    self.send_mail('Last inverter data older than 24h', msg, message_id=message_id, in_reply_to=True)
                    self.set_sent_mail('timeout', inv['serial'], message_id, sent=False)
            time.sleep(interval)

    def send_mail(self, subject, message, message_id=None, in_reply_to=False, debug=False ):
        if len(self.mail_config["recipients"]) > 0:
            smtp_server = self.mail_config["smtp_server"]
            sender = self.mail_config["sender"]
            recipients = self.mail_config["recipients"]
            starttls = self.mail_config["starttls"]

            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = ", ".join(recipients)

            if message_id is not None:
                if not in_reply_to:
                    msg['Message-ID'] = message_id
                    msg['Subject'] = "sunportal: %s" % subject
                else:
                    msg['In-Reply-To'] = message_id
                    msg['Subject'] = "RE: sunportal: %s" % subject
            else:
                msg['Subject'] = "sunportal: %s" % subject

            msg.attach(MIMEText(message))

            # image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
            # image = add_header('Content-ID', '<image1>')
            # msg.attach(image)

            with smtplib.SMTP(smtp_server["url"], port=smtp_server["port"]) as s:
                if debug: s.set_debuglevel(1)
                if starttls and starttls["enabled"]:
                    s.starttls()
                    s.login(starttls["user"], starttls["password"])
                s.sendmail(sender, recipients, msg.as_string())

    def set_sent_mail(self, type, identifier, message_id, sent=True):
        if type not in self.sent_messages: self.sent_messages[type] = { identifier: dict() }
        if sent:
            self.sent_messages[type][identifier] = {
                'action': 'sent',
                'time': datetime.now(),
                'message_id': message_id
            }
        else:
            self.sent_messages[type][identifier] = {
                'action': 'cleared',
                'time': datetime.now(),
                'message_id': message_id
            }

    def do_send_mail(self, type, identifier):
        if type not in self.sent_messages: return True
        if identifier not in self.sent_messages[type]: return True
        i = self.sent_messages[type][identifier]
        if i['action'] == 'sent' and i['time'] < (datetime.now() - timedelta(hours=24)):
            return True
        if i['action'] == 'cleared':
            return True
        return False

    def do_send_clear_mail(self, type, identifier):
        if type not in self.sent_messages: return False
        if identifier not in self.sent_messages[type]: return False
        i = self.sent_messages[type][identifier]
        if i['action'] == 'sent': return True
        return False

    def get_message_id(self, type, identifier):
        if type not in self.sent_messages: return None
        if identifier not in self.sent_messages[type]: return None
        return self.sent_messages[type][identifier]['message_id']

    def join(self):
        self.stop_threads = True

if __name__ == '__main__':

    from database import Database
    from config import Config

    cfg = Config(config_path='../config.json')
    db = Database(cfg)

    mail = Mail(cfg, db)
    mail.send_mail('test mail', 'this is your test mail', debug=True)