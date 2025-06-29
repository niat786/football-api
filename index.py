from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from typing import Union
from mangum import Mangum  # AWS Lambda adapter
import base64
import httpx


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/fetch-menus")
async def fetch_diaries():
    url = "https://ftvhd.com/diaries.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; DiariesFetcher/1.0)"
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return JSONResponse(status_code=response.status_code, content={
                "error": f"Failed to fetch diaries.json. Status code: {response.status_code}"
            })

        # Parse JSON response
        data = response.json() 

        return {"data": data['data']}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/get-embed-link")
def get_embed(raw_iframe_url: str = Query(...)):
    # Parse the 'r' query parameter
    parsed_url = urlparse(raw_iframe_url)
    query_params = parse_qs(parsed_url.query)
    encoded_url = query_params.get("r", [""])[0]
    
    # Decode Base64
    try:
        decoded_bytes = base64.urlsafe_b64decode(encoded_url)
        decoded_url = decoded_bytes.decode("utf-8")
    except Exception:
        decoded_url = None

    # Final clean response
    return JSONResponse({
        "original_embed_iframe": raw_iframe_url,
        "decoded_url": decoded_url
    })

# Required by Vercel's serverless system
handler = Mangum(app)
