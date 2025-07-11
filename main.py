from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from typing import Union
import base64
import httpx
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow localhost:8888
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # or ["*"] for all domains (not recommended in production)
    allow_credentials=True,
    allow_methods=["*"],              # or specify: ["GET", "POST"]
    allow_headers=["*"],              # or specify: ["Content-Type", "Authorization"]
)

@app.get("/")
def root():
    return {"message": "Hello from FastAPI on Vercel"}

@app.get("/fetch-menus")
async def fetch_diaries():
    # url = "https://ftvhd.com/diaries.json"
    url = "https://golazoplay.com/agenda.json"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return JSONResponse(status_code=response.status_code, content={
                "error": f"Failed to fetch diaries.json. Status code: {response.status_code}"
            })

        data = response.json()
        return {"data": data.get("data")}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/get-embed-link")
def get_embed(raw_iframe_url: str = Query(...)):
    parsed_url = urlparse(raw_iframe_url)
    query_params = parse_qs(parsed_url.query)
    encoded_url = query_params.get("r", [""])[0]

    try:
        decoded_bytes = base64.urlsafe_b64decode(encoded_url)
        decoded_url = decoded_bytes.decode("utf-8")
    except Exception:
        decoded_url = None

    return JSONResponse({
        "original_embed_iframe": raw_iframe_url,
        "decoded_url": decoded_url
    })