# LinkedIn Extractor POC

An AI-powered LinkedIn data extraction tool that uses browser automation and OpenAI's GPT-4o to extract information from LinkedIn profiles and pages.

## Features

- 🚀 FastAPI endpoint for easy integration
- 🌐 Browser automation with Selenium
- 📸 Full-page screenshot capture
- 🤖 AI-powered data extraction using OpenAI GPT-4o
- 📊 Structured JSON output
- 🔒 Secure API key management

## Prerequisites

- Python 3.8+
- Chrome browser installed
- OpenAI API key
- LinkedIn account (for accessing profiles)

## Installation

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

4. **Install Chrome WebDriver (automatically handled by webdriver-manager)**

## Usage

### Starting the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

### API Endpoints

#### 1. Health Check
```bash
GET http://localhost:8000/health
```

#### 2. Extract LinkedIn Data
```bash
POST http://localhost:8000/extract
```

**Request Body:**
```json
{
  "url": "https://www.linkedin.com/in/username/",
  "description": "Extract all available information from this LinkedIn profile"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "John Doe",
    "title": "Software Engineer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "about": "Experienced software engineer...",
    "experience": [...],
    "education": [...],
    "skills": [...],
    "metadata": {
      "source_url": "https://www.linkedin.com/in/username/",
      "screenshot_path": "screenshots/linkedin_123456.png",
      "extraction_timestamp": 1234567890.123
    }
  },
  "message": "Data extracted successfully"
}
```

### Example Usage with curl

```bash
curl -X POST "http://localhost:8000/extract" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://www.linkedin.com/in/username/",
       "description": "Extract all profile information"
     }'
```

### Example Usage with Python

```python
import requests

url = "http://localhost:8000/extract"
data = {
    "url": "https://www.linkedin.com/in/username/",
    "description": "Extract all available information"
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

## How It Works

1. **URL Reception**: The FastAPI endpoint receives a LinkedIn URL
2. **Browser Automation**: Selenium opens the URL in Chrome browser
3. **Screenshot Capture**: Takes a full-page screenshot of the LinkedIn page
4. **AI Analysis**: Sends the screenshot to OpenAI GPT-4o for analysis
5. **Data Extraction**: AI extracts structured data from the screenshot
6. **JSON Response**: Returns the extracted data in JSON format

## Important Notes

### LinkedIn Authentication
- The browser will open in visible mode by default
- You need to manually log in to LinkedIn in the browser window
- The browser will remember your session for subsequent requests
- To run in headless mode, uncomment the headless option in `linkedin_extractor.py`

### Rate Limiting
- Be mindful of LinkedIn's rate limits
- Consider adding delays between requests
- Respect LinkedIn's terms of service

### Screenshots
- Screenshots are saved in the `screenshots/` directory
- Each screenshot is named with a hash of the URL
- Screenshots are automatically cleaned up (you may want to implement cleanup logic)

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `CHROME_HEADLESS`: Set to "true" for headless mode (optional)
- `SCREENSHOT_DIR`: Custom screenshot directory (optional)

### Browser Options

You can modify browser options in `linkedin_extractor.py`:
- Window size
- User agent
- Headless mode
- Additional Chrome flags

## Troubleshooting

### Common Issues

1. **Chrome WebDriver Issues**
   - Ensure Chrome is installed
   - The webdriver-manager will automatically download the correct driver

2. **OpenAI API Issues**
   - Verify your API key is correct
   - Check your OpenAI account balance
   - Ensure you have access to GPT-4o

3. **LinkedIn Access Issues**
   - Make sure you're logged into LinkedIn
   - Some profiles may be private or restricted
   - Consider using a LinkedIn Premium account for better access

4. **Screenshot Issues**
   - Ensure the screenshots directory is writable
   - Check if the page loads completely before screenshot

### Debug Mode

Enable debug logging by modifying the logging level in `linkedin_extractor.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

- Never commit your `.env` file to version control
- Keep your OpenAI API key secure
- Be aware of LinkedIn's terms of service
- Consider implementing rate limiting
- Validate input URLs

## Future Enhancements

- [ ] Add authentication and rate limiting
- [ ] Implement screenshot cleanup
- [ ] Add support for multiple LinkedIn page types
- [ ] Cache extracted data
- [ ] Add webhook support for async processing
- [ ] Implement retry logic for failed requests
- [ ] Add data validation and sanitization

## License

This project is for educational and POC purposes. Please ensure compliance with LinkedIn's terms of service and applicable laws. 