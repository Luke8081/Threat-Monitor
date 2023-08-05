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
    #Installs zap. Then runs file
    os.system("wget -O zap_installer.sh https://github.com/zaproxy/zaproxy/releases/download/v2.13.0/ZAP_2_13_0_unix.sh && chmod +x zap_installer.sh && ./zap_installer.sh")

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

    conn.execute('''CREATE TABLE IF NOT EXISTS execution_time
            (Date           DATE   NOT NULL,
            Time           REAL    NOT NULL);''')

    conn.close()

def banner():
    print(text2art("Automated\n Vulnerabillity\n Scanner"))
    print(text2art("Author: Luke"))

def install_req():
    #Download pip 
    os.system('apt install python3-pip')
    #Download the requirements 
    os.system("pip install -r requirements.txt")

def setup_http_server():
    os.chdir(os.getcwd() + '/http-server')
    os.system('apt install nodejs')
    os.system('apt install npm')
    os.system('npm install express sqlite3')
    os.system('npm install')
    os.chdir("../")



if __name__ == "__main__":
    #Checks the user is root. If they are asks if they want to download the zap server
    if os.geteuid()==0:
        print("Would you like to install Zap server(y/n)?")
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

    if os.geteuid()==0:
        #Install packages for web server
        setup_http_server()

    from art import *
    banner()
    




    
    



