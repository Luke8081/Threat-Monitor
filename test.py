import requests

'''
headers = {
'Accept': 'application/json',
'X-ZAP-API-Key': 'hs7kfbo68e7exuo94pmcz0pg2',
}

#http://127.0.0.1:8080/JSON/reports/action/generate/?apikey=hs7kfbo68e7exuo94pmcz0pg2&title=Scan report&template=Risk and Confidence&theme=&description=&contexts=&sites=&sections=&includedConfidences=&includedRisks=&reportFileName=&reportFileNamePattern=&reportDir=&display=



#New one with values filed
#http://127.0.0.1:8080/JSON/reports/action/generate/?apikey=hs7kfbo68e7exuo94pmcz0pg2&title=Scanner&template=Risk+and+Confidence+HTML&theme=Originam&description=THis+is+a+test&contexts=&sites=https%3A%2F%2Fpublic-firing-range.appspot.com&sections=&includedConfidences=Low+%7C+Medium+%7C+High&includedRisks=Low+%7C+Medium+%7C+High&reportFileName=&reportFileNamePattern=%7B%7Byyyy-MM-dd%7D%7D-ZAP-Report-%5B%5Bsite%5D%5D&reportDir=%2Fhome%2Fvboxuser&display=true
params = {
    'apikey': 'hs7kfbo68e7exuo94pmcz0pg2',
    'title':'ZAP Scanning Report',
    'template':'Risk and Confidence HTML',
    'theme':'',
    'description':'',
    'contexts':'',
    'sites':'',
    'sections':'',
    'includedConfidences':'',
    'includedRisks':'',
    'reportFileName':'',
    'reportFileNamePattern':'',
    'reportDir':'',
    'display':'',
}

response = requests.get(f"http://127.0.0.1:8080/UI/reports/action/generate/", , headers = headers, params= params)
#response = requests.get('http://127.0.0.1:8080/JSON/reports/action/generate/?apikey=hs7kfbo68e7exuo94pmcz0pg2&title=Scan report&template=Risk and Confidence&theme=&description=&contexts=&sites=&sections=&includedConfidences=&includedRisks=&reportFileName=&reportFileNamePattern=&reportDir=&display=')
print(response.content)
print(response.json())

#with open('test.html', 'w') as file:
#   file.write(response.content.decode())

'''

#Connect to API and download html report
headers = {
    'Accept': 'application/json',
    'X-ZAP-API-Key': 'hs7kfbo68e7exuo94pmcz0pg2',
}

response = requests.get(f"http://127.0.0.1:8080/OTHER/core/other/htmlreport/", headers = headers)

print(response.content.decode('utf-8'))