#!/usr/bin/env python3
"""
LinkedIn Login Helper - Facilitates first-time login process
"""

import asyncio
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
er logging in, the session will be saved for future requests.")
    print()
    
    # Initialize extractor
    extractor = LinkedInExtractor()
    
    try:
        # Setup browser for login (temporarily use visible mode)
        print("🌐 Opening browser for login setup...")
        
        # Temporarily override headless mode for login
        original_headless = True  # Default is headless
        if hasattr(extractor, 'playwright') and extractor.playwright:
            # If browser is already running, we need to close it and restart in visible mode
            await extractor.close_browser()
        
        # Create a temporary visible browser for login
        extractor.playwright = await extractor.playwright.__class__().start()
        user_data_dir = os.path.join(os.getcwd(), "browser_data")
        os.makedirs(user_data_dir, exist_ok=True)
        
        extractor.browser_context = await extractor.playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,  # Visible for login
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1920,1080"
            ]
        )
        
        pages = extractor.browser_context.pages
        if pages:
            extractor.page = pages[0]
        else:
            extractor.page = await extractor.browser_context.new_page()
        
        await extractor.page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        # Check if already logged in
        print("🔍 Checking if already logged in...")
        await extractor.page.goto("https://www.linkedin.com/feed/")
        await asyncio.sleep(3)
        
        if "login" not in extractor.page.url and "auth" not in extractor.page.url:
            print("✅ Already logged in to LinkedIn!")
            print("You can now use the API to extract data from LinkedIn profiles.")
            return
        
        # Navigate to LinkedIn login page
        print("📱 Navigating to LinkedIn...")
        await extractor.page.goto("https://www.linkedin.com/login")
        
        print("\n" + "=" * 50)
        print("🔑 MANUAL LOGIN REQUIRED")
        print("=" * 50)
        print("1. You should see the LinkedIn login page in the browser")
        print("2. Enter your LinkedIn email/username and password")
        print("3. Complete any 2FA if prompted")
        print("4. Wait for the page to fully load after login")
        print("5. Press Enter here when you're logged in and ready")
        print("=" * 50)
        
        # Wait for user to complete login
        input("Press Enter when you're logged in to LinkedIn...")
        
        # Verify login by checking if we're on LinkedIn
        current_url = extractor.page.url
        if "linkedin.com" in current_url:
            print("✅ Successfully logged in to LinkedIn!")
            print(f"Current URL: {current_url}")
            
            # Test with a simple LinkedIn page
            print("\n🧪 Testing with LinkedIn homepage...")
            await extractor.page.goto("https://www.linkedin.com/feed/")
            await asyncio.sleep(3)
            
            print("✅ Login setup completed successfully!")
            print("You can now use the API to extract data from LinkedIn profiles.")
            
        else:
            print("⚠️  Warning: Doesn't appear to be on LinkedIn. Please check your login.")
            
    except Exception as e:
        print(f"❌ Error during login setup: {str(e)}")
        raise
        
    finally:
        # Keep browser open for a moment so user can see the result
        print("\n⏳ Keeping browser open for 5 seconds...")
        await asyncio.sleep(5)
        
        # Close browser
        if hasattr(extractor, 'browser_context'):
            await extractor.browser_context.close()
        if hasattr(extractor, 'playwright'):
            await extractor.playwright.stop()
        print("🔒 Browser closed")

async def check_login_status():
    """Check if we can access LinkedIn without login"""
    print("🔍 Checking LinkedIn access...")
    
    extractor = LinkedInExtractor()
    
    try:
        await extractor.setup_browser()
        
        # Try to access LinkedIn feed (requires login)
        await extractor.page.goto("https://www.linkedin.com/feed/")
        await asyncio.sleep(3)
        
        current_url = extractor.page.url
        
        if "login" in current_url or "auth" in current_url:
            print("❌ Not logged in - you'll need to log in manually")
            return False
        else:
            print("✅ Already logged in to LinkedIn!")
            return True
            
    except Exception as e:
        print(f"❌ Error checking login status: {str(e)}")
        return False
        
    finally:
        if hasattr(extractor, 'browser_context'):
            await extractor.browser_context.close()
        if hasattr(extractor, 'playwright'):
            await extractor.playwright.stop()

async def main():
    """Main function"""
    print("🚀 LinkedIn Login Helper")
    print("=" * 30)
    
    # Check if OpenAI is available
    if not OPENAI_AVAILABLE:
        print("\n❌ Cannot proceed without proper OpenAI setup.")
        print("Please ensure:")
        print("1. You have set up your .env file with OPENAI_API_KEY")
        print("2. Your OpenAI API key is valid")
        print("3. All dependencies are installed correctly")
        print("\nTo fix this, run:")
        print("pip install -r requirements.txt --upgrade")
        return
    
    # Check if already logged in
    if await check_login_status():
        print("\n🎉 You're already logged in! You can start using the API.")
        return
    
    print("\n📋 Login Setup Options:")
    print("1. Setup LinkedIn login (opens browser)")
    print("2. Skip setup (you'll login manually when using the API)")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        await setup_linkedin_login()
    else:
        print("\n✅ Skipping setup. You'll be prompted to login when you first use the API.")
        print("To use the API, run: python main.py")

if __name__ == "__main__":
    asyncio.run(main()) 
