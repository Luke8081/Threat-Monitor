import smtplib, os
from email.message import EmailMessage
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)

# start TLS for security
s.starttls()

# Authentication
s.login("zap.warning.alert@gmail.com", os.getenv("EMAIL_PASSWD"))

html = f'''
            <html>
                <body style="  margin: auto;width: 50%;border: 3px solid red;padding: 10px;">
                    <h1 style="color:red;">High security risk found</h1>
                </body>
            </html>
            '''

file = open('/home/luke/Coda/reports/public-firing-range.appspot.com/2023-05-12.html', 'r')
report = file.read()
file.close()

report = html + report

email_message = MIMEMultipart()
email_message['From'] = "zap.warning.alert@gmail.com"
email_message['To'] = os.getenv("TO_EMAIL")
email_message['Subject'] = f'ACTION NEEDED'

email_message.attach(MIMEText(report, "html"))
# Convert it as a string
email_string = email_message.as_string()

s.sendmail("zap.warning.alert@gmail.com", os.getenv("TO_EMAIL"), email_string)
s.quit()