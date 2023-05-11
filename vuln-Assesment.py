from datetime import datetime
from urllib.parse import urlparse
import time
from pprint import pprint
from zapv2 import ZAPv2
import requests, os.path


class Assesment:
    def __init__(self, addresses, verbose):

        self.API_key = 'goqjhdjmm0vid6f7v2uftgn68d'
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
        

        if bool(high_Alert) and self.alarm == True:

            for i in range(6):
                os.system('play -nq -t alsa synth {} sine {}'.format(0.3, 700))
                time.sleep(0.2)
        
           

        
        #Add alert count to the total
        self.alert_count = high_Alert + medium_Alert + low_Alert
    


        


        
    


def main():
    
    #Read addresses from file and store as list
    addresses = open('addresses.txt', 'r').read().split('\n')
    
    test = Assesment(addresses, verbose=False)
    test.run_Assesment()
    test.log()

if __name__ == "__main__":
    main()

    


