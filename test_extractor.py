#!/usr/bin/env python3
"""
Test script for LinkedIn Extractor POC
"""

import asyncio
import json
from linkedin_extractor import LinkedInExtractor

async def test_linkedin_extraction():
    """Test the LinkedIn extraction functionality"""
    
    # Test URL (replace with a real LinkedIn profile URL)
    test_url = "https://www.linkedin.com/in/username/"
    test_description = "Extract all available information from this LinkedIn profile"
    
    print("🚀 Starting LinkedIn Extractor Test")
    print(f"📋 Test URL: {test_url}")
    print(f"📝 Description: {test_description}")
    print("-" * 50)
    
    try:
        # Initialize extractor
        extractor = LinkedInExtractor()
        
        # Extract data
        print("🔄 Extracting data...")
        result = await extractor.extract_data(test_url, test_description)
        
        # Display results
        print("✅ Extraction completed successfully!")
        print("\n📊 Extracted Data:")
        print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Error during extraction: {str(e)}")
        raise

def test_openai_connection():
    """Test OpenAI API connection"""
    import os
    from openai import OpenAI
    
    print("🔍 Testing OpenAI API connection...")
    
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            max_tokens=10
        )
        
        print("✅ OpenAI API connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {str(e)}")
        return False

def test_browser_setup():
    """Test browser setup"""
    print("🌐 Testing browser setup...")
    
    try:
        extractor = LinkedInExtractor()
        extractor.setup_browser()
        
        # Test navigation to a simple page
        extractor.driver.get("https://www.google.com")
        title = extractor.driver.title
        
        print(f"✅ Browser setup successful! Page title: {title}")
        
        # Clean up
        extractor.driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Browser setup failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🧪 LinkedIn Extractor POC - Test Suite")
    print("=" * 50)
    
    # Test 1: OpenAI Connection
    print("\n1️⃣ Testing OpenAI API Connection...")
    openai_ok = test_openai_connection()
    
    # Test 2: Browser Setup
    print("\n2️⃣ Testing Browser Setup...")
    browser_ok = test_browser_setup()
    
    # Test 3: Full Extraction (only if previous tests pass)
    if openai_ok and browser_ok:
        print("\n3️⃣ Testing Full Extraction...")
        await test_linkedin_extraction()
    else:
        print("\n⚠️  Skipping full extraction test due to previous failures")
    
    print("\n🏁 Test suite completed!")

if __name__ == "__main__":
    asyncio.run(main()) 