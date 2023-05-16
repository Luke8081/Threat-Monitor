import cronitor, time, os
from dotenv import load_dotenv

load_dotenv()

cronitor.api_key = os.getenv("CRONITOR_API_KEY")
cronitor.Monitor.put(
    key='test',
    type='job',
    notify=['Luke-8081'],
    schedule="0 0 * * 1",
    assertions= ["metric.duration < 10 min"]
)

@cronitor.job("test")
def main1():
    time.sleep(10)



main1()