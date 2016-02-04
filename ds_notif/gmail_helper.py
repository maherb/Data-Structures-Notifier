import smtplib, imaplib, html_helper
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

config_path = "C:/ds_notif/account_config.txt"
recip_path = "C:/ds_notif/recip_list.txt"

signature = '\n\n-Brian Maher\nmaherb@rpi.edu'
signature += '\n\nEmail data.structures.notifier@gmail.com with subject "subscribe" to subscribe or "unsubscribe" to unsubscribe.'
signature += '\nPlease contact me via my RPI email address with questions, comments, or feedback.'

welcome_subject = "Welcome to Data Structures Notifications!"
welcome_message = "You will recieve emails when labs and homeworks are posted to the course calendar. I hope you find this utility useful!" + signature

notif_subject = "New Data Structures assignment: %s"
notif_message = "A new Data Structures assignment, %s, has been posted to the calendar: %s" + signature

remove_subject = "You have unsubscribed from Data Structures Notifications"
remove_message = "You will no longer receive Data Structures Notification emails. Good luck in Data Structures and the rest of your endeavors!" + signature

nc_subject = "Invalid command for Data Structures Notifier"
nc_message = "Your message is not a valid command." + signature

def account_data():
	account_data = open(config_path).readlines()
	return account_data[0].strip(), account_data[1].strip()

def read_recip_set():
	return eval(open(recip_path, 'r').read())

def write_recip_set(recip_set):
	open(recip_path, 'w').write(repr(recip_set))

def send_mail(to_address, subject, msg_text):
	file_data = open(config_path).readlines()
	username = file_data[0].strip()
	password = file_data[1].strip()

	msg = MIMEMultipart()
	msg['From'] = username
	msg['To'] = to_address
	msg['Subject'] = subject
	msg.attach(MIMEText(msg_text, 'plain'))

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(username, password)
	server.sendmail(username, to_address, msg.as_string())
	server.quit()

def send_mail_list(subject, msg_text, address_set):
	username, password = account_data()

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(username, password)

	for to_address in address_set:
		msg = MIMEMultipart()
		msg['From'] = username
		msg['To'] = to_address
		msg['Subject'] = subject
		msg.attach(MIMEText(msg_text, 'plain'))
		print "-Sending message to %s" % to_address
		server.sendmail(username, to_address, msg.as_string())
	
	server.quit()

def get_addresses_update():
	username, password = account_data()
	add, remove, other = set(), set(), set()

	server = imaplib.IMAP4_SSL('imap.gmail.com', 993)
	server.login(username, password)
	server.select("INBOX")
	result, data = server.search(None, "ALL")
	if result == "OK":
		for num in data[0].split():
			print num
			result, fetched_data = server.fetch(num, "(BODY[HEADER.FIELDS (SUBJECT FROM)])")
			fetched_data_list = fetched_data[0][1].split("\r\n")
			from_info = fetched_data_list[0].replace("From: ", "", 1)
			subject = fetched_data_list[1].replace("Subject: ", "", 1)
			from_address = from_address_helper(from_info)
			print subject, from_address
			if subject.lower() == "subscribe":
				add.add(from_address)
			elif subject.lower() == "unsubscribe":
				remove.add(from_address)
			else:
				other.add(from_address)
			server.store(num, '+FLAGS', '\\Deleted')
	else:
		pass
		#this will be an error of some sort
	return add, remove, other

def update_subscriptions():
	add, remove, other = get_addresses_update()
	recip_set = read_recip_set()

	if len(add) > 0:
		recip_set = recip_set | add
		print "*Subscribing:"
		send_mail_list(welcome_subject, welcome_message, add)

	if len(remove) > 0:
		recip_set = recip_set - remove
		print "*Unsubscribing:"
		send_mail_list(remove_subject, remove_message, remove)

	if len(other) > 0:
		print "*Non-command notification:"
		send_mail_list(nc_subject, nc_message, other)
	write_recip_set(recip_set)

def notify_assignment(assign):
	print "-Assignment: %s" % assign
	subject = notif_subject % assign
	msg_text = notif_message % (assign, html_helper.calendar_url)
	send_mail_list(subject, msg_text, read_recip_set())

def from_address_helper(from_info):
	addr_begin = from_info.find("<")
	addr_end = from_info.find(">")
	return from_info[addr_begin+1:addr_end]

if __name__ == "__main__":
	update_subscribers()