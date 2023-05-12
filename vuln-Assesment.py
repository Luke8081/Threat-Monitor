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
        'X-ZAP-API-Key': self.API_key
        }

        response = requests.get(f"http://127.0.0.1:8080/OTHER/core/other/htmlreport/", params={
        }, headers = headers)

        if (response.status_code == 200):
            file_name = f"{dir_name}/{self.date}.html"
            file = open(file_name, 'w')
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


        if bool(high_Alert) and self.send_email:

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
                <body>
                     <img src="data:image/jpeg;base64,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" alt="Warning image" width="500" height="600"> 
                    <h1 style="color:red;">High risk security issue found</h1>
                </body>
            </html>
            '''

        file = open('/home/luke/Coda/reports/public-firing-range.appspot.com/2023-05-12.html', 'r')
        report = file.read()
        file.close()

        report = report + html

        email_message = MIMEMultipart()
        email_message['From'] = "zap.warning.alert@gmail.com"
        email_message['To'] = os.getenv("TO_EMAIL")
        email_message['Subject'] = f'ACTION NEEDED'

        email_message.attach(MIMEText(report, "html"))
        # Convert it as a string
        email_string = email_message.as_string()

        s.sendmail("zap.warning.alert@gmail.com", os.getenv("TO_EMAIL"), email_string)
        s.quit()

    


        


        
    


def main():
    
    #Read addresses from file and store as list
    addresses = open('addresses.txt', 'r').read().split('\n')
    
    test = Assesment(addresses, verbose=False, send_email=True)
    test.run_Assesment()
    test.log()

if __name__ == "__main__":
    main()

    


