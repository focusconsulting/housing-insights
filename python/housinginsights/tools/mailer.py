import sys
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

secrets_filepath = os.path.join(os.path.dirname(__file__), "../secrets.json")
import json

with open(secrets_filepath) as fh:
    secrets = json.load(fh)

COMMASPACE = ", "


class HIMailer:
    def __init__(self, recipients=[], cc_recipients=[], debug_mode=False, **kwargs):
        self.properties = kwargs
        self.debug_mode = debug_mode
        self.recipients = recipients
        self.cc_recipients = cc_recipients
        self.debug_recipient = secrets["email"]["debug_recipient"]
        self.send_from = secrets["email"]["username"]
        self.username = secrets["email"]["username"]
        self.password = secrets["email"]["password"]
        self.host = secrets["email"]["host"]
        self.admin_email = secrets["email"].get("admin", "")
        self.attachments = None

    def send_email(self):
        # Create the enclosing (outer) message
        outer = MIMEMultipart("alternative")
        outer["Subject"] = self.subject
        outer["From"] = self.send_from
        if self.debug_mode:
            outer["To"] = self.debug_recipient
        else:
            self.recipients.append(self.admin_email)
            outer["To"] = COMMASPACE.join(self.recipients)
            outer["CC"] = COMMASPACE.join(self.cc_recipients)

        msg = MIMEBase("application", "octet-stream")

        # Add the text of the email
        email_body = MIMEText(self.message, "plain")
        outer.attach(email_body)

        # Add the attachments
        if self.attachments:
            for file in self.attachments:
                try:
                    with open(file, "rb") as fp:
                        msg.set_payload(fp.read())
                    encoders.encode_base64(msg)
                    msg.add_header(
                        "Content-Disposition",
                        "attachment",
                        filename=os.path.basename(file),
                    )
                    outer.attach(msg)
                except:
                    print("Unable to add the attachment to the email")
                    raise

        composed = outer.as_string()

        if self.debug_mode:
            all_recipients = [self.debug_recipient]
        else:
            all_recipients = set(self.recipients + self.cc_recipients)
            all_recipients = list(filter(None, all_recipients))

        if not all_recipients:
            raise ValueError("No recipients provided, unable to send email.")

        try:
            with smtplib.SMTP(host=self.host, port="587") as s:
                s.ehlo()
                s.starttls()
                s.login(self.username, self.password)
                s.sendmail(self.username, all_recipients, composed)
                s.close()
                print("Email successfully sent.")
        except smtplib.SMTPConnectError as err:
            print("Unable to connect to the SMTP server to send email: {}".format(err))
            raise
        except:
            print("Unable to send email: {}".format(sys.exc_info()[0]))
            raise


if __name__ == "__main__":
    pass
