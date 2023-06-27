import os.path, os, time, random, string
#Run this file to set up application 


def make_env_file():
    zap_api = ''.join(random.choices(string.ascii_lowercase + string.digits, k=25))
    email = input("Enter email to send alerts to (not required): ")
    email_pass = input("Enter email password (not required): ")
    cronitor_api = input("Enter cronitor API key (not required): ")


    file = open('.env', 'w')
    file.write(f"API_KEY={zap_api}\n")
    file.write(f"CRONITOR_API_KEY={cronitor_api}\n")
    file.write(f"TO_EMAIL={email}\n")
    file.write(f"EMAIL_PASSWD={email_pass}\n")
    file.close()

    print("Created enviroment varibles")
    print(f"File saved to: {os.getcwd()}/.env")

def install_Zap():
    print("Downloading Zap and required packages")
    os.system("apt install default-jre")
    os.system("apt install snapd -y")
    os.system("snap install zaproxy --classic")

def set_database():
    import sqlite3

    #Creates database file if one does not exist
    if os.path.isfile("reports/database.db") == False:
        os.system("touch reports/database.db")
    
    #Connect to database and create a table.
    conn = sqlite3.connect("reports/database.db")
    conn.execute('''CREATE TABLE IF NOT EXISTS alert_Summary
            (Address         TEXT    NOT NULL,
            Low_Alert       INT     NOT NULL,
            Medium_Alert    INT     NOT NULL,
            High_Alert      INT     NOT NULL,
            Date            DATE    NOT NULL);''')
    conn.close()

def banner():
    print(text2art("Automated\n Vulnerabillity\n Scanner"))
    print(text2art("Author: Luke"))

def install_req():
    #Download the requirements 
    os.system("pip install -r requirements.txt")



if __name__ == "__main__":
    #Checks the user is root. If they are asks if they want to download the zap server
    if os.geteuid()==0:
        print("Would you like to install Zap server and required packages(y/n)?")
        if input() == "y":
            install_Zap()
    else:
        print("WARNING: This file must be run as root to install Zap and required packages")

    #Check if enviroment file exists if not set it up
    if os.path.isfile(".env") == False:
        make_env_file()
    
    #Set up database
    set_database()
    
    #Install all required python packages
    print("Would you like to install required python packages(y/n)?")
    if input() == "y":
        install_req()
    
    from art import *
    banner()
    




    
    



