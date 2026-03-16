from google import genai
client = genai.Client(api_key="AIzaSyBkYHDtY1SdDVOGzzbgq79fL40cZHHPJkQ")
for m in client.models.list():
    print(f"Modelo disponible: {m.name}")