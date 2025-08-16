import requests
import os
from dotenv import load_dotenv

load_dotenv()

# def google_search(api_key, search_engine_id, query, limit):
#     url = "https://www.googleapis.com/customsearch/v1"
#     params = {
#         'key': api_key,
#         'cx': search_engine_id,
#         'q': query,
#         'num': limit  # Set the number of results per request (max 10)
#     }
#     response = requests.get(url, params=params)
#     return response.json()

def google_search(query, limit):
    url = "https://duckduckgo8.p.rapidapi.com/"
    querystring = {"q": query }

    headers = {
        "x-rapidapi-host": "duckduckgo8.p.rapidapi.com",
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY")
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        
        # Handle specific HTTP status codes
        if response.status_code == 403:
            print("API Key error: Check if your RapidAPI key is valid and active")
            return []
        elif response.status_code == 429:
            print("Rate limit exceeded: Too many requests to the API")
            return []
        elif response.status_code != 200:
            print(f"HTTP Error {response.status_code}: {response.text}")
            return []
        
        data = response.json()
        print("API Response keys:", data.keys())
        print("API Response:", data)
        
        # Handle different possible response structures
        if 'results' in data:
            return data['results'][:limit]
        elif 'data' in data:
            return data['data'][:limit]
        elif 'items' in data:
            return data['items'][:limit]
        else:
            # If none of the expected keys exist, return an empty list
            print(f"Unexpected API response structure: {data}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return []
    except KeyError as e:
        print(f"Key error in response: {e}")
        print(f"Response data: {response.json() if response.status_code == 200 else 'No response'}")
        return []
    except Exception as e:
        print(f"Unexpected error in google_search: {e}")
        return []

# Example usage
# api_key = 'AIzaSyDWQdpxZHM7Zpft2tMJ_1olqoXthQrlXfo'
# search_engine_id = '82bd22c03bc644768'
# comp_name = 'Whoop'
# position = 'VP'
# query = f'''Present {position} at {comp_name} AND site:linkedin.com'''
# results = google_search(query, limit=5)  # Set limit to 5

# print(results)
# Process results
# for item in results.get('items', []):
#     title = item.get('title')
#     snippet = item.get('snippet')
#     print(f'Title: {title}\nSnippet: {snippet}\n') 