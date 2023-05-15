import requests, os
from dotenv import load_dotenv

load_dotenv()

API = os.getenv("API_KEY")
site = 'public-firing-range.appspot.com:443'

'''
#View current sites which have a session
headers = {
  'Accept': 'application/json',
  'X-ZAP-API-Key': API
}

r = requests.get('http://127.0.0.1:8080/JSON/httpSessions/view/sites/', params={

}, headers = headers)

print("Sessions: ", r.json())



#View sessions to a site
def view_sesh():
    headers = {
    'Accept': 'application/json',
    'X-ZAP-API-Key': API
    }

    r = requests.get('http://127.0.0.1:8080/JSON/httpSessions/view/defaultSessionTokens/', params={
    }, headers = headers)

    print("Current sessions: ", r.json())


#Create new session
headers = {
  'Accept': 'application/json',
  'X-ZAP-API-Key': API
}

r = requests.get('http://127.0.0.1:8080/JSON/httpSessions/action/createEmptySession/', params={
    'site':site, 'session': 'test'
}, headers = headers)

print("New session: ", r.json())


#View the active session for the site
headers = {
  'Accept': 'application/json',
  'X-ZAP-API-Key': API
}

r = requests.get('http://127.0.0.1:8080/JSON/httpSessions/view/activeSession/', params={
  'site': site
}, headers = headers)

print(r.json())
'''

#Delete the active session
headers = {
  'Accept': 'application/json',
  'X-ZAP-API-Key': API
}

r = requests.get('http://127.0.0.1:8080/JSON/httpSessions/action/removeSession/', params={
  'site': site, 'session': 'test'
}, headers = headers)

print('Deleted session: ', r.json())


#View the active session for the site
headers = {
  'Accept': 'application/json',
  'X-ZAP-API-Key': API
}

r = requests.get('http://127.0.0.1:8080/JSON/httpSessions/view/activeSession/', params={
  'site': site
}, headers = headers)

print(r.json())




#Get report for site
headers = {
  'Accept': 'application/json',
  'X-ZAP-API-Key': API
}

r = requests.get('http://127.0.0.1:8080/OTHER/core/other/htmlreport/', params={
}, headers = headers)

print(r.status_code)

open('test.html', 'wb').write(r.content)

