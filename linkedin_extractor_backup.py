import asyncio
import os
import base64
import json
from typing import Dict, Any
from playwright.async_api import async_playwright
from PIL import Image
import io
import openai
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInExtractor:
    def __init__(self):
        """Initialize the LinkedIn extractor with OpenAI client and browser setup"""
        # Initialize OpenAI client with error handling
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please add it to your .env file.")
        
        try:
            self.openai_client = openai.OpenAI(api_key=api_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {str(e)}. Please check your API key and try upgrading dependencies with 'pip install -r requirements.txt --upgrade'")
        
        # Browser session management
        self.playwright = None
        self.browser_context = None
        self.page = None
        self.screenshots_dir = "screenshots"
        
        # Create screenshots directory if it doesn't exist
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
    async def setup_browser(self):
        """Setup Playwright browser with appropriate options for LinkedIn"""
        try:
            # Only setup if not already initialized
            if self.playwright is None:
                self.playwright = await async_playwright().start()
                
                # Create user data directory for session persistence
                user_data_dir = os.path.join(os.getcwd(), "browser_data")
                os.makedirs(user_data_dir, exist_ok=True)
                
                # Launch persistent browser context
                self.browser_context = await self.playwright.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=True,  # Run in headless mode for production
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--window-size=1920,1080"
                    ]
                )
                
                # Get the first page or create a new one
                pages = self.browser_context.pages
                if pages:
                    self.page = pages[0]
                else:
                    self.page = await self.browser_context.new_page()
                
                # Set user agent
                await self.page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                })
                
                logger.info("Browser setup completed with Playwright (session persistence enabled)")
            else:
                logger.info("Browser session already active")
            
        except Exception as e:
            logger.error(f"Failed to setup browser: {str(e)}")
            raise Exception(f"Failed to setup browser with Playwright: {str(e)}")
        
    async def take_screenshot(self, url: str) -> str:
        """Navigate to URL and take a full-page screenshot"""
        try:
            logger.info(f"Navigating to: {url}")
            await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for page to load completely
            await asyncio.sleep(5)
            
            # Check if we need to login
            current_url = self.page.url
            if "login" in current_url or "auth" in current_url:
                logger.warning("LinkedIn login required! Please log in manually in the browser window.")
                print("\n" + "=" * 60)
                print("🔑 LINKEDIN LOGIN REQUIRED")
                print("=" * 60)
                print("The browser window has opened to LinkedIn.")
                print("Please log in manually with your LinkedIn credentials.")
                print("After logging in, the page will automatically refresh.")
                print("=" * 60)
                
                # Wait for user to login (max 2 minutes)
                wait_time = 0
                while ("login" in self.page.url or "auth" in self.page.url) and wait_time < 120:
                    await asyncio.sleep(2)
                    wait_time += 2
                    if wait_time % 10 == 0:
                        print(f"⏳ Waiting for login... ({wait_time}s elapsed)")
                
                if "login" in self.page.url or "auth" in self.page.url:
                    raise Exception("Login timeout - please try again")
                
                # Navigate back to the original URL after login
                await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(5)
            
            # Take full page screenshot
            screenshot_path = os.path.join(self.screenshots_dir, f"linkedin_{hash(url)}.png")
            await self.page.screenshot(path=screenshot_path, full_page=True)
            
            logger.info(f"Screenshot saved to: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            raise
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Convert image to base64 for OpenAI API"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            raise
    
    async def analyze_screenshot_with_openai(self, image_path: str, description: str) -> Dict[str, Any]:
        """Send screenshot to OpenAI for analysis and data extraction"""
        try:
            # Encode image to base64
            base64_image = self.encode_image_to_base64(image_path)
            
            # Prepare the prompt for OpenAI
            prompt = f"""
            Analyze this LinkedIn screenshot and extract all available information in JSON format.
            
            Description: {description}
            
            Please extract the following information if available:
            - Name
            - Title/Position
            - Company
            - Location
            - About/Summary
            - Experience (jobs, companies, dates)
            - Education
            - Skills
            - Contact information
            - Profile picture URL
            - Any other relevant information
            
            Return the data in a clean JSON format. If any field is not available, set it to null.
            """
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            # Try to parse JSON from the response
            try:
                # Look for JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = content[start_idx:end_idx]
                    extracted_data = json.loads(json_str)
                else:
                    # If no JSON found, create a structured response
                    extracted_data = {
                        "raw_response": content,
                        "extraction_status": "manual_parsing_required"
                    }
                    
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw response
                extracted_data = {
                    "raw_response": content,
                    "extraction_status": "json_parsing_failed"
                }
            
            logger.info("OpenAI analysis completed")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error analyzing screenshot with OpenAI: {str(e)}")
            raise
    
    async def extract_data(self, url: str, description: str = "Extract all available information") -> Dict[str, Any]:
        """Main method to extract data from LinkedIn URL"""
        try:
            logger.info(f"Starting extraction for URL: {url}")
            
            # Ensure browser is setup (should already be done at startup)
            if self.page is None:
                await self.setup_browser()
            
            # Take screenshot
            screenshot_path = await self.take_screenshot(url)
            
            # Analyze with OpenAI
            extracted_data = await self.analyze_screenshot_with_openai(screenshot_path, description)
            
            # Add metadata
            extracted_data["metadata"] = {
                "source_url": url,
                "screenshot_path": screenshot_path,
                "extraction_timestamp": asyncio.get_event_loop().time()
            }
            
            logger.info("Data extraction completed successfully")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error in data extraction: {str(e)}")
            raise
    
    async def close_browser(self):
        """Close the browser session"""
        try:
            if self.browser_context:
                await self.browser_context.close()
                self.browser_context = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            logger.info("Browser session closed")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}") 