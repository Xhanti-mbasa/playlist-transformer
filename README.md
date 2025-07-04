## Spotify ↔ YouTube Music Playlist Converter

***A bi-directional music playlist converter that allows you to transfer your music library between Spotify and YouTube Music using browser-based authentication (no API keys required).***
✨ Features

    Bi-directional conversion: Spotify → YouTube Music and YouTube Music → Spotify
    Browser-based authentication: No API keys or developer credentials needed
    Multiple content types: Convert playlists, liked songs, albums, and followed artists
    Fuzzy matching: Intelligent track matching with manual correction options
    Local processing: All data stays on your device - nothing is sent externally
    Modern web interface: Clean, responsive UI built with FastAPI

## 🚀 Quick Start
Prerequisites

    - Python 3.8 or higher
    - Chrome browser installed
    - ChromeDriver (will be auto-downloaded by Selenium)

## Installation

 **Clone or download the project**
    
  
    git clone https://github.com/Xhanti-mbasa/playlist-transformer.git
    cd playlist-transformer

Install dependencies

    pip install -r requirements.txt

    Run the application

    python api.py

    Open your browser Navigate to http://localhost:8000

🔧 Troubleshooting
Browser Window Closes Too Quickly

If the browser window opens for authentication but closes immediately:

    Check the console output - The application now includes detailed logging
    Use the Cancel button - If authentication fails, use the "Cancel Authentication" button to properly close the browser
    Restart the application - If you encounter issues, restart the Python application

Authentication Issues

    Make sure you're using the correct login credentials
    Some platforms may require 2FA - complete the verification in the browser window
    The browser window will stay open until authentication is complete or you cancel

📖 Usage Guide
## Step 1: Choose Direction

    Select whether you want to convert from Spotify to YouTube Music or vice versa
    Click "Start Conversion"

## Step 2: Authenticate

    The app will open browser windows for authentication
    Log in to your accounts when prompted
    The app will automatically capture your session

## Step 3: Select Content

    Browse your library (playlists, liked songs, albums, artists)
    Select the items you want to convert
    Click "Continue"

## Step 4: Review Matches

    Review the automatic matches found on the target platform
    Correct any mismatches using the manual correction feature
    Deselect any unwanted tracks

## Step 5: Create Playlist

    Confirm your selection
    The app will create a new playlist on the target platform
    You'll receive a link to your new playlist

## 🏗️ Architecture

## The application is built with a modular architecture:

    api.py: FastAPI server with all endpoints and session management
    auth_browser.py: Browser automation for authentication
    fetch_spotify.py: Spotify library scraping using Selenium
    fetch_ytm.py: YouTube Music API integration
    match_engine.py: Fuzzy matching logic using thefuzz
    converter.py: Data transformation between platforms
    templates/: HTML templates for the web interface

🔧 Configuration
Environment Variables (Optional)

# Chrome options
CHROME_HEADLESS=true  # Run browser in background
CHROME_TIMEOUT=30     # Authentication timeout in seconds

# Matching settings
CONFIDENCE_THRESHOLD=70  # Minimum confidence for auto-matching

Customization

    Adjust matching confidence threshold in match_engine.py
    Modify browser options in auth_browser.py
    Customize UI styling in template files

## 🛠️ Development
Project Structure


<pre><code>```text spotify-ytm-converter/ ├── api.py # Main FastAPI application ├── auth_browser.py # Browser authentication ├── fetch_spotify.py # Spotify data fetching ├── fetch_ytm.py # YouTube Music data fetching ├── match_engine.py # Fuzzy matching engine ├── converter.py # Data conversion utilities ├── requirements.txt # Python dependencies ├── README.md # This file └── templates/ # HTML templates ├── index.html # Landing page ├── library.html # Library selection ├── matches.html # Match review └── auth.html # Authentication page ``` </code></pre>

Adding New Features

    New platform support: Create new fetcher class following the existing pattern
    Enhanced matching: Extend match_engine.py with additional algorithms
    UI improvements: Modify templates and add new endpoints in api.py

## 🔒 Security & Privacy

    No data storage: All session data is kept in memory and cleared after conversion
    Local processing: No music data is sent to external servers
    Browser automation: Uses your own browser session for authentication
    No API keys: Authentication handled through browser login flows

## 🐛 Troubleshooting
Common Issues

Authentication fails

    Ensure Chrome browser is installed and up to date
    Check that ChromeDriver is compatible with your Chrome version
    Try running without headless mode for debugging

No tracks found

    Verify you're logged into the correct account
    Check that your library has content to convert
    Some content may be region-restricted

Poor matching results

    Adjust the confidence threshold in match_engine.py
    Use manual correction for important tracks
    Check for typos in track/artist names

Debug Mode

Run with debug logging:

python api.py --log-level debug

**📝 License**


This project is open source and available under the MIT License.


***🤝 Contributing***


Contributions are welcome! Please feel free to submit a Pull Request.



***⚠️ Disclaimer***


This tool is for personal use only. Please respect the terms of service of both Spotify and YouTube Music. The developers are not responsible for any misuse of this application.
