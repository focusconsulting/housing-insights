import smtplib, ssl
from ETL.utils import get_credentials

def send_mail(receivers, message):
    '''Sends an email.'''
    password = get_credentials('email-password')
    text = f'Subject: Housing Insights Data Update\n\n{message}'
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login("housinginsights@gmail.com", password)
        for receiver_email in receivers:
            server.sendmail("housinginsights@gmail.com", receiver_email, text)

if __name__ == '__main__':
    message = 'This message is sent from Python.'
    receivers = get_credentials('email-receivers')
    send_mail(receivers, message)
