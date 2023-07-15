from charset_normalizer import md__mypyc
from os import path, mkdir
from requests import Session
import random
import string
import pickle 


SESSION_FILE = 'account/session.pkl'
session = None
if path.exists(SESSION_FILE):
	with open(SESSION_FILE, 'rb') as f: session = pickle.load(f) 


# print error
def display_error(response, message):
	print(message)
	print(response)
	print(response.text)


# login and format
def format_data(content_type, fields):
	data = ""
	for name, value in fields.items():
		data += f"--{content_type}\x0d\x0aContent-Disposition: form-data; name=\"{name}\"\x0d\x0a\x0d\x0a{value}\x0d\x0a"
	data += content_type+"--"
	return data

def login(email, password):
	session = Session()
	session.get("https://archive.org/account/login")
	content_type = "----WebKitFormBoundary"+"".join(random.sample(string.ascii_letters + string.digits, 16))

	headers = {'Content-Type': 'multipart/form-data; boundary='+content_type}
	data = format_data(content_type, {"username":email, "password":password, "submit_by_js":"true"})

	response = session.post("https://archive.org/account/login", data=data, headers=headers)
	if "bad_login" in response.text:
		print("[-] Invalid credentials!")
		return None
	elif "Successful login" in response.text:
		print("[+] Successful login")
		return session
	else:
		display_error(response, "[-] Error while login:")
		return None
		

# get book
def loan(book_id):
	global session
	if not session:
		with open(SESSION_FILE, 'rb') as f: session = pickle.load(f) 
	data = {
		"action": "grant_access",
		"identifier": book_id
	}
	response = session.post("https://archive.org/services/loans/loan/searchInside.php", data=data)
	data['action'] = "browse_book"
	response = session.post("https://archive.org/services/loans/loan/", data=data)

	if response.status_code == 400 :
		if response.json()["error"] == "This book is not available to borrow at this time. Please try again later.":
			print("This book doesn't need to be borrowed")
			return session
		else :
			display_error(response, "Something went wrong when trying to borrow the book.")
			return None

	data['action'] = "create_token"
	response = session.post("https://archive.org/services/loans/loan/", data=data)

	if "token" in response.text:
		print("[+] Successful loan")
		return session
	else:
		display_error(response, "Something went wrong when trying to borrow the book, maybe you can't borrow this book.")
		return None

# acsm file
def get_acsmfile(bookid,format="pdf"):
	global session
	if not session:
		with open(SESSION_FILE, 'rb') as f: session = pickle.load(f)
		
	response = session.get(f"https://archive.org/services/loans/loan/?action=media_url&format={format}&redirect=1&identifier={bookid}")
	
	if response.status_code == 200:
		with open(f"{bookid}.acsm","w") as af: af.write(response.text)
		return f"{bookid}.acsm"
	else: 
		display_error(response, "Something went wrong when trying to get ACSM")
		return None


# return the book
def return_loan(book_id):
	global session
	if not session:
		with open(SESSION_FILE, 'rb') as f: session = pickle.load(f) 
	data = {
		"action": "return_loan",
		"identifier": book_id
	}
	response = session.post("https://archive.org/services/loans/loan/", data=data)
	if response.status_code == 200 and response.json()["success"]:
		print("[+] Book returned")
		return True
	else:
		display_error(response, "Something went wrong when trying to return the book")
		return None


# manage
def manage_login(email,password):
    global session
    if not path.exists('account'): mkdir('account')
    sess = login(email,password)
    if sess is not None: 
        with open(SESSION_FILE, 'wb') as f: pickle.dump(sess, f)
        session = sess

def get_book(url,format):
    global session
    bookid = url.split("/")[4]
    sess = loan(bookid)
    if sess is not None: 
        with open(SESSION_FILE, 'wb') as f: pickle.dump(sess, f)
        session = sess
        return get_acsmfile(bookid,format)
    return None

def return_book(url):
	bookid = url.split("/")[4]
	return return_loan(bookid)
