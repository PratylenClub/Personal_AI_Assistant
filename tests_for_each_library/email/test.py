import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

import imaplib

def read(username, password, sender_of_interest):
    # Login to INBOX
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    imap.login(username, password)
    imap.select('INBOX')
    
    status, response = imap.search(None, '(UNSEEN)')
    unread_msg_nums = response[0].split()

    # Print the count of all unread messages
    print len(unread_msg_nums)

    # Print all unread messages from a certain sender of interest
    status, response = imap.search(None, '(UNSEEN)', '(FROM "%s")' % (sender_of_interest))
    unread_msg_nums = response[0].split()
    da = []
    for e_id in unread_msg_nums:
        _, response = imap.fetch(e_id, '(UID BODY[TEXT])')
        da.append(response[0][1])
    print da

    # Mark them as seen
    for e_id in unread_msg_nums:
        imap.store(e_id, '+FLAGS', '\Seen')
    


 

def send(username, password, receptor_of_interest):
    msg = MIMEMultipart()
 
    msg['From'] = username
    msg['To'] = receptor_of_interest
    msg['Subject'] = "SUBJECT OF THE EMAIL"
 
    body = "TEXT YOU WANT TO SEND"
     
    msg.attach(MIMEText(body, 'plain'))
     
    filename = "NAME OF THE FILE WITH ITS EXTENSION"
    attachment = open("test.py", "rb")
 
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= " + filename)
     
    msg.attach(part)
 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, password)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

