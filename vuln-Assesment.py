from datetime import datetime
from urllib.parse import urlparse
from threading import Thread
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time, subprocess
from pprint import pprint
from zapv2 import ZAPv2
import requests, os.path, smtplib
from dotenv import load_dotenv
import cronitor, json, sqlite3



#Load enviroment varibles
load_dotenv()

class Assesment:
    def __init__(self, addresses, verbose, send_email, debug):

        self.API_key = os.getenv("API_KEY")
        self.email_passwd = os.getenv("EMAIL_PASSWD")
        self.to_email = os.getenv("TO_EMAIL")
        self.send_email = send_email
        self.verbose = verbose
        self.addresses = addresses
        self.date = datetime.today().strftime('%Y-%m-%d')
        self.date_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        self.address_counter = 0
        self.alert_count = 0 
        self.debug = debug
        self.high_Risk = False
        self.alarm = False
        self.zap = None
        self.conn = sqlite3.connect("reports/database.db")

        #Debug mode is very verbose
        if self.debug:
            self.verbose = True
        

        #Test to see if zap server is already running
        #If it is shut it down. There could ne multiple zap servers running.
        #They all need to be shut down to make sure port 8080 is open
        zap_proxy_state = Assesment.test_Zap(debug=self.debug, test_once=True)
        while zap_proxy_state:
            headers = {
            'Accept': 'application/json',
            'X-ZAP-API-Key': self.API_key,
            }
            response = requests.get("http://127.0.0.1:8080/JSON/core/action/shutdown/", params={}, headers=headers)
            if response.json()['Result'] != "OK":
                raise Exception("Failed to shutdown Zap server.", response.json())
            time.sleep(5)
            zap_proxy_state = Assesment.test_Zap(debug=self.debug, test_once=True)

        if zap_proxy_state and self.verbose:
            print("Zap server already online. Shutting server down")

        #Creates thread to start zap in the background. Needs to be on another thread to run
        if self.verbose:
            print("Starting zap server")

        start_thread = Thread(target=self.start_zap, daemon=True)
        start_thread.start()

        if self.verbose:
            print('Waiting for Zap server...')

        Assesment.test_Zap(debug=self.debug, test_once=False)

                

        #Connects to API. Connects to 127.0.0.1 on port 8080
        if self.verbose:
            print("Zap server is online")
        count = 0 
        while self.zap == None:
            try:
                self.zap = ZAPv2(apikey=self.API_key)
                if self.zap:
                    print("Connected to Zap server")
            except:
                if count == 5:
                    raise Exception("Could not connect to Zap server")
                count+=1
                time.sleep(2)

    def start_zap(self):
        #Start zap server
        if self.debug:
            cmd = f"/usr/local/bin/zap.sh -daemon -config api.key={self.API_key}"
        else:
            cmd = f"/usr/local/bin/zap.sh -daemon -nostdout -config api.key={self.API_key}"
        subprocess.run(cmd, shell=True)
    
    def test_Zap(debug=False, test_once=False):
        conection = True
        count = 0
        while conection:
            try:
                response = requests.get("http://127.0.0.1:8080/")
                conection = False
                if debug:
                    print("Waiting...")
                return True
            except Exception as e:
                time.sleep(1)
                count += 1
                if test_once:
                    return False
                if count ==40:
                    raise Exception("Zap server did not start")
    
    def active_Scan(self, address):

        fileName = f"{address}_{self.date}"

        #Gets all of the sites directories
        self.spider(address)

        #Start the active scan
        
        scanID = self.zap.ascan.scan(address)

        if self.verbose:
            print('Active Scanning target {}'.format(address))
            while int(self.zap.ascan.status(scanID)) < 100:
                # Loop until the scanner has finished
                print('Scan progress : {}%'.format(self.zap.ascan.status(scanID)))
                time.sleep(2)
            print('Active Scan completed')
        else:
            while int(self.zap.ascan.status(scanID)) < 100:
                time.sleep(2)
        
        
        if self.debug:
            # Print vulnerabilities found by the scanning
            pprint('Hosts: {}'.format(', '.join(self.zap.core.hosts)))
            print('Alerts: ')
            pprint(self.zap.core.alerts(baseurl=address))
        
        #Get a report of the scan
        self.get_Report(address)
        #Get any alerts 
        self.get_Alerts(address)
        



    def spider(self, address):

        scanID = self.zap.spider.scan(address)

        if self.verbose:
            print(f'Spidering target {address}')
            
            #Prints the progress
            while int(self.zap.spider.status(scanID)) < 100:
                print('Spider progress %: {}'.format(self.zap.spider.status(scanID)))
                time.sleep(1)
            print('Spider has completed!')
            # Prints the URLs the spider has crawled
        else:
            while int(self.zap.spider.status(scanID)) < 100:
                time.sleep(2)

        if self.debug:
            print('\n'.join(map(str, self.zap.spider.results(scanID))))
    
    def run_Assesment(self):
        start_timer = time.perf_counter()

        #Loop through address and scan each one and time how long it takes
        for address in self.addresses:
            if address == "":
                raise Exception('Make sure there are no extra lines in addresses file')
            self.active_Scan(address)
            self.address_counter += 1

        #Shutdown zap server
        self.zap.core.shutdown()
            
        stop_timer = time.perf_counter()
        self.time = round(stop_timer - start_timer, 2)
    
    def log(self):

        #Check that assesment has been run before trying to log
        if hasattr(self, 'time') == False:
            raise Exception("Run assesment before recording log")
        
        msg = f"\nScanned {self.address_counter} addresses in {self.time} seconds. Number of alerts: {self.alert_count}. Completed on {self.date_time}."

        if self.medium_Alert:
            msg = msg + " - ACTION NEEDED."

        print(msg)

        dir_name = os.getcwd() + "/reports/"

        file = open('scan_log.txt', 'a')
        file.write(msg)
        file.close()
    
    def get_Report(self, address):

        #Get the domain name
        dir_name = urlparse(address).netloc
        dir_name = os.getcwd() + "/reports/" + dir_name
        dir_JSON = dir_name + "/JSON"
        #Checks if the directory exist. If not it creates it
        dir_exist = os.path.isdir(dir_name)
        if dir_exist == False:
            os.mkdir(dir_name)
            os.mkdir(dir_JSON)
        
        #Connect to API and download html report
        headers = {
        'Accept': 'application/json',
        'X-ZAP-API-Key': self.API_key,
        'sites': address
        }

        response = requests.get(f"http://127.0.0.1:8080/OTHER/core/other/htmlreport/", params={
        }, headers = headers)

        if (response.status_code == 200):
            self.file_name = f"{dir_name}/{self.date}.html"
            file = open(self.file_name, 'w')
            file.write(response.content.decode('utf-8'))
            file.close()
            if (self.verbose):
                print("\nCreated HTML report. Directory: ", self.file_name)
        else:
            raise Exception("Failed to get report. Couldn't connect to API")

        #Connect to API and download JSON report

        headers = {
        'Accept': 'application/json',
        'X-ZAP-API-Key': self.API_key,
        'sites': address
        }

        response = requests.get(f"http://127.0.0.1:8080/OTHER/core/other/jsonreport/", params={
        }, headers = headers)

        if (response.status_code == 200):
            self.file_name = f"{dir_JSON}/{self.date}.json"
            with open(self.file_name, 'w') as file:
                json.dump(response.json(), file)

            if (self.verbose):
                print("\nCreated JSON report. Directory: ", self.file_name)
        else:
            raise Exception("Failed to get report. Couldn't connect to API")
    
    def get_Alerts(self, address_full):
        
        address = urlparse(address_full).netloc

        #Get the a summary of the zap scan.
        params = {'apikey': self.API_key}

        resp = requests.get(f'http://127.0.0.1:8080/JSON/alert/view/alertsSummary/',
                            params=params)

        if (resp.status_code == 200):
            json_response = resp.json()
            resp = json_response["alertsSummary"]

            self.high_Alert = resp.get("High")
            self.medium_Alert = resp.get("Medium")
            self.low_Alert = resp.get("Low")
        else:
            raise Exception(f'Failed to get the summary. {str(resp.status_code)}')
        

        #Add alert count to the total
        self.alert_count = self.high_Alert + self.medium_Alert + self.low_Alert

        #Store the results in the database
        self.insert_or_update_scan(address)


        if bool(self.high_Alert) and self.send_email:
            self.send_alert_email()
        
    def insert_or_update_scan(self, address):
        #Set up connection to the data base
        cursor = self.conn.cursor()

        params = (address, self.low_Alert, self.medium_Alert, self.high_Alert, self.date)

        #Store the reults to the database. If the address already exists then update the results
        cursor.execute('SELECT Address FROM alert_Summary WHERE Address = ?', (address,))
        exists_row = cursor.fetchone()

        if exists_row is None:
            sql = f'''INSERT INTO alert_Summary('Address','Low_Alert', 'Medium_Alert', 'High_Alert', 'Date')
            VALUES(?,?,?,?,?)'''
        else:
            sql = '''UPDATE alert_Summary SET Address = ?, Low_Alert = ?, Medium_Alert = ?, High_Alert = ?, Date = ?'''

        if self.debug:
            print('Writing results to database...')

        cursor.execute(sql, params)

        self.conn.commit()
        self.conn.close()

        if self.debug:
            print('Results successfully stored to database')
           

        

    
    def send_alert_email(self):
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

        file = open(self.file_name, 'r')
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

        if self.verbose:
            print("\nSending alert email")
        s.sendmail("zap.warning.alert@gmail.com", os.getenv("TO_EMAIL"), email_string)
        s.quit()

#Set up cronitor. If you don't want to use cronitor delete the cronitor code
# and the decoration around the main function.
cronitor.api_key = os.getenv("CRONITOR_API_KEY")
cronitor.Monitor.put(
    key='vuln-Assesment',
    type='job',
    schedule="0 0 * * 1",
    assertions= ["metric.duration < 10 min"]
)

@cronitor.job("vuln-Assesment")
def main():
    #Read addresses from file and store as list
    #raise Exception("This is a test")
    addresses = open(f'{os.getcwd()}/addresses.txt', 'r').read().split('\n')
    test = Assesment(addresses, verbose=True, send_email=False, debug=False)
    test.run_Assesment()
    test.log()

if __name__ == "__main__":
    main()

    


