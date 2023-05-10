from datetime import datetime
import time, subprocess, os
from pprint import pprint
from zapv2 import ZAPv2


class Assesment:
    def __init__(self, addresses):

        self.API_key = ''
        self.addresses = addresses
        self.date = datetime.today().strftime('%Y-%m-%d')
        self.date_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        self.address_counter = 0
        
    
    def scan_Website(self, address):
        '''
        #Scan website and record the output in a file
        fileName = f"{address}_{self.date}"
        #Create file
        open("fileName", "w").close()
        to_run = f"./zap.sh {address} -daemon -quickurl -quickout {fileName}.html"
        subprocess.Popen(to_run)'''



        
        zap = ZAPv2(apikey=self.API_key, proxies={'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'})

        scanID = zap.ascan.scan(address)
        while int(zap.ascan.status(scanID)) < 100:
            # Loop until the scanner has finished
            print('Scan progress %: {}'.format(zap.ascan.status(scanID)))
            time.sleep(5)

        print('Active Scan completed')
        # Print vulnerabilities found by the scanning
        print('Hosts: {}'.format(', '.join(zap.core.hosts)))
        print('Alerts: ')
        pprint(zap.core.alerts(baseurl=address))
    
    def scan_Ports():
        pass
    
    def run_Assesment(self):
        start_timer = time.perf_counter()

        #Loop through address and scan each one and time how long it takes
        for address in self.addresses:
            self.scan_Website(address)
            self.address_counter += 1
            
        stop_timer = time.perf_counter()
        self.time = round(stop_timer - start_timer, 2)
    
    def log(self):
        #Check that assesment has been run before trying to log
        if hasattr(self, 'time') == False:
            raise Exception("Run assesment before recording log")
        
        msg = f"\nScanned {self.address_counter} addresses in {self.time} seconds. Completed on {self.date_time}\n"
        print(msg)

        file = open('scan_log.txt', 'a')
        file.write(msg)
        file.close()
        
    


def main():
    address_counter = 0
    #Read addresses from file and store as list
    addresses = open('addresses.txt', 'r').read().split('\n')
    
    test = Assesment(addresses)
    test.run_Assesment()
    test.log()

if __name__ == "__main__":
    main()

    


