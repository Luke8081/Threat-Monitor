import smtplib

# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)

# start TLS for security
s.starttls()

# Authentication
s.login("zap.warning.alert@gmail.com", "")

# message to be sent
message = "THis is a test email"

# sending the mail
s.sendmail("zap.warning.alert@gmail.com", "L.com", message)

# terminating the session
s.quit()
