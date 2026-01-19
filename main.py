from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from scraper import VidangeScraper
import uvicorn

app = FastAPI(
    title="Plate Scraper API",
    description="API to scrape car details from vidange.tn",
    version="1.0.0"
)

class ScrapeRequest(BaseModel):
    plate_type: str = "TUN"  # "TUN" or "RS"
    serie: Optional[str] = ""
    num: Optional[str] = ""
    num_rs: Optional[str] = ""

class ScrapeResponse(BaseModel):
    status: str
    data: List[Dict]

@app.get("/")
async def root():
    return {"message": "Welcome to the Plate Scraper API. Use /scrape to get car details."}

@app.get("/scrape/tun/{serie}/{num}", response_model=ScrapeResponse)
async def scrape_tun(serie: str, num: str):
    try:
        scraper = VidangeScraper(
            plate_type="TUN",
            serie=serie,
            num=num
        )
        data = scraper.run()
        
        if not data:
            return {"status": "no_data", "data": []}
            
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scrape/rs/{num_rs}", response_model=ScrapeResponse)
async def scrape_rs(num_rs: str):
    try:
        scraper = VidangeScraper(
            plate_type="RS",
            num_rs=num_rs
        )
        data = scraper.run()
        
        if not data:
            return {"status": "no_data", "data": []}
            
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
