from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import uvicorn
from linkedin_extractor import LinkedInExtractor
import os
from dotenv import load_dotenv
import asyncio
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Global extractor instance
extractor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for browser session"""
    global extractor
    try:
        # Startup
        extractor = LinkedInExtractor()
        await extractor.setup_browser()
        print("🚀 Browser session initialized successfully!")
        yield
    finally:
        # Shutdown
        if extractor:
            await extractor.close_browser()
            print("🔒 Browser session closed")

app = FastAPI(
    title="LinkedIn Extractor POC",
    description="AI-powered LinkedIn profile data extraction using screenshots",
    version="1.0.0",
    lifespan=lifespan
)

class LinkedInURLRequest(BaseModel):
    url: HttpUrl
    description: str = "Extract all available information from this LinkedIn profile or page"

class LinkedInExtractionResponse(BaseModel):
    success: bool
    data: dict
    message: str

@app.get("/")
async def root():
    return {"message": "LinkedIn Extractor POC - Send a POST request to /extract with a LinkedIn URL"}

@app.post("/extract", response_model=LinkedInExtractionResponse)
async def extract_linkedin_data(request: LinkedInURLRequest):
    """
    Extract data from a LinkedIn URL by taking a screenshot and analyzing it with OpenAI
    """
    global extractor
    
    try:
        # Initialize the extractor if not already done
        if extractor is None:
            extractor = LinkedInExtractor()
            await extractor.setup_browser()
        
        # Extract data from the LinkedIn URL
        extracted_data = await extractor.extract_data(
            url=str(request.url),
            description=request.description
        )
        
        return LinkedInExtractionResponse(
            success=True,
            data=extracted_data,
            message="Data extracted successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract data: {str(e)}"
        )

@app.post("/close-browser")
async def close_browser():
    """Close the browser session"""
    global extractor
    
    try:
        if extractor:
            await extractor.close_browser()
            extractor = None
        return {"message": "Browser session closed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to close browser: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "LinkedIn Extractor POC"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 