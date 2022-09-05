import alpha_vantage
import requests
import datetime
url = "https://electricity-carbon-footprint-germany.p.rapidapi.com/gridde"
headers = {
	"X-RapidAPI-Key": "b0eea21866mshdab03fbc603d458p12fb40jsnc2498116f547",
	"X-RapidAPI-Host": "electricity-carbon-footprint-germany.p.rapidapi.com"
}

def get_current_co2_footprint():

    today = datetime.datetime.today()
    print(today)
    querystring = {"date": today.__repr__()}
    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)

if __name__ == "__main__":
    get_current_co2_footprint()

