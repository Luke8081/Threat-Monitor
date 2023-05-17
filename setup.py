import os.path, os, time
#Run this file to set up application 


def make_env_file():
    email = input("Enter email to send alerts to: ")
    email_pass = input("Enter email password: ")
    zap_api = input("Enter zap API key: ")
    cronitor_api = input("Enter cronitor API key: ")


    file = open('.env', 'w')
    file.write(f"API_KEY={zap_api}\n")
    file.write(f"CRONITOR_API_KEY={cronitor_api}\n")
    file.write(f"TO_EMAIL={email}\n")
    file.write(f"EMAIL_PASSWD={email_pass}\n")
    file.close()


def banner():
    print(text2art("Automated\n Vulnerabillity\n Scanner"))
    print(text2art("Author: Luke"))

def install_req():
    #Download the requirements 
    os.system("pip install -r requirements.txt")

if __name__ == "__main__":
    #Check if file exists if not set it up
    if os.path.isfile(".env") == False:
        make_env_file()
        print("Created enviroment varibles")
    
    print("Would you like to install required packages(y/n):")
    if input() == "y":
        install_req()
    
    from art import *
    banner()
    




    
    



