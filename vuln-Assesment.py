from datetime import datetime
import time, subprocess, os
from pprint import pprint
from zapv2 import ZAPv2


class Assesment:
    def __init__(self, addresses, verbose):

        self.API_key = 'goqjhdjmm0vid6f7v2uftgn68d'
        self.verbose = verbose
        self.addresses = addresses
        self.date = datetime.today().strftime('%Y-%m-%d')
        self.date_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        self.address_counter = 0
        
    
    def active_Scan(self, address):

        fileName = f"{address}_{self.date}"
        #Create file
        open("fileName", "w").close()

        #Gets all of the sites directories
        self.spider(address)



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

    
    def scan_Ports():
        pass
    
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
        
        msg = f"\nScanned {self.address_counter} addresses in {self.time} seconds. Completed on {self.date_time}\n"
        print(msg)

        file = open('scan_log.txt', 'a')
        file.write(msg)
        file.close()
        
    


def main():
    address_counter = 0
    #Read addresses from file and store as list
    addresses = open('addresses.txt', 'r').read().split('\n')
    
    test = Assesment(addresses, verbose=True)
    test.run_Assesment()
    test.log()

if __name__ == "__main__":
    main()

    


