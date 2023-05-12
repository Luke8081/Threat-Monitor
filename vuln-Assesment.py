from datetime import datetime
from urllib.parse import urlparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
from pprint import pprint
from zapv2 import ZAPv2
import requests, os.path, smtplib
from dotenv import load_dotenv

#Load enviroment varibles
load_dotenv()


class Assesment:
    def __init__(self, addresses, verbose, send_email):

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
        self.high_Risk = False
        self.alarm = False
        
    
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
                print('Scan progress %: {}'.format(self.zap.ascan.status(scanID)))
                time.sleep(2)

            print('Active Scan completed')
            # Print vulnerabilities found by the scanning
            pprint('Hosts: {}'.format(', '.join(self.zap.core.hosts)))
            print('Alerts: ')
            pprint(self.zap.core.alerts(baseurl=address))
        else:
            while int(self.zap.ascan.status(scanID)) < 100:
                time.sleep(2)
        
        #Get a report of the scan
        self.get_Report(address)
        #Get any alerts 
        self.get_Alerts()
        



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
            print('\n'.join(map(str, self.zap.spider.results(scanID))))
        else:
            while int(self.zap.spider.status(scanID)) < 100:
                time.sleep(2)
    
    def run_Assesment(self):
        start_timer = time.perf_counter()

        #Connects to API. Connects to 127.0.0.1 on port 8080
        self.zap = ZAPv2(apikey=self.API_key)

        #Loop through address and scan each one and time how long it takes
        for address in self.addresses:
            self.active_Scan(address)
            self.address_counter += 1
            
        stop_timer = time.perf_counter()
        self.time = round(stop_timer - start_timer, 2)
    
    def log(self):

        #Check that assesment has been run before trying to log
        if hasattr(self, 'time') == False:
            raise Exception("Run assesment before recording log")
        
        msg = f"\nScanned {self.address_counter} addresses in {self.time} seconds. Number of alerts: {self.alert_count}. Completed on {self.date_time}."

        if self.high_Risk:
            msg = msg + " - ACTION NEEDED"

        print(msg)

        dir_name = os.getcwd() + "/reports/"

        file = open('scan_log.txt', 'a')
        file.write(msg)
        file.close()
    
    def get_Report(self, address):

        #Get the domain name
        dir_name = urlparse(address).netloc
        dir_name = os.getcwd() + "/reports/" + dir_name
        #Checks if the directory exist. If not it creates it
        dir_exist = os.path.isdir(dir_name)
        if dir_exist == False:
            os.mkdir(dir_name)
        
        #Connect to API and download report

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
                print("\nCreated HTML report. Directory: ", dir_name)
        else:
            raise Exception("Failed to get report. Couldn't connect to API")
    
    def get_Alerts(self):

        #Get the a summary of the zap scan.
        params = {'apikey': self.API_key}

        resp = requests.get(f'http://127.0.0.1:8080/JSON/alert/view/alertsSummary/',
                            params=params)

        if (resp.status_code == 200):
            json_response = resp.json()
            resp = json_response["alertsSummary"]

            high_Alert = resp.get("High")
            medium_Alert = resp.get("Medium")
            low_Alert = resp.get("Low")
        else:
            raise Exception(f'Failed to get the summary. {str(resp.status_code)}')
        

        #Add alert count to the total
        self.alert_count = high_Alert + medium_Alert + low_Alert


        if bool(medium_Alert) and self.send_email:
            self.send_alert_email()
        
        
           

        

    
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

    


        


        
    


def main():
    
    #Read addresses from file and store as list
    addresses = open('addresses.txt', 'r').read().split('\n')
    
    test = Assesment(addresses, verbose=True, send_email=True)
    test.run_Assesment()
    test.log()

if __name__ == "__main__":
    main()

    


