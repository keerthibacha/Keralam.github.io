import requests

url = "https://order-tracking.p.rapidapi.com/carriers"

headers = {
	"Content-Type": "application/json",
	"X-RapidAPI-Key": "8b0bb7663amshb42b25fd64ad8d0p164a19jsn362f1f341f87",
	"X-RapidAPI-Host": "order-tracking.p.rapidapi.com"
}

response = requests.request("GET", url, headers=headers)

print(response.text)