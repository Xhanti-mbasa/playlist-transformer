from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
import os
from typing import Dict, Optional

class AuthManager:
    def __init__(self):
        self.driver = None
        self.spotify_cookies = None
        self.ytm_cookies = None
        self._keep_alive = False  # Flag to prevent automatic closure
        
    def _setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def start_spotify_auth(self) -> str:
        """Start Spotify authentication process"""
        if not self.driver:
            self._setup_driver()
            
        # Set flag to keep browser alive during auth process
        self._keep_alive = True
            
        # Navigate to Spotify login
        self.driver.get("https://accounts.spotify.com/login")
        
        # Wait for login form and return current URL
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-username"))
        )
        
        return self.driver.current_url
        
    def complete_spotify_auth(self) -> bool:
        """Complete Spotify authentication and extract cookies"""
        try:
            print("Waiting for Spotify authentication to complete...")
            
            # Wait for successful login (redirect to Spotify)
            WebDriverWait(self.driver, 30).until(
                lambda driver: any(pattern in driver.current_url for pattern in [
                    "open.spotify.com",
                    "accounts.spotify.com/authorize",
                    "spotify.com/authorize",
                    "spotify.com/login",
                    "spotify.com/account",
                    "accounts.spotify.com/en/status",  # Status page after authentication
                    "accounts.spotify.com/status",     # Alternative status page
                    "challenge.spotify.com"            # Challenge pages (email verification, etc.)
                ])
            )
            
            print(f"Spotify authentication successful. Current URL: {self.driver.current_url}")
            
            # Extract cookies
            self.spotify_cookies = self.driver.get_cookies()
            print(f"Extracted {len(self.spotify_cookies)} Spotify cookies")
            
            # Save cookies to file for later use
            with open("spotify_cookies.json", "w") as f:
                json.dump(self.spotify_cookies, f)
            
            # Don't close the browser yet - let the status checking handle it
            # self._keep_alive = False
            # self.close_driver()
                
            return True
            
        except Exception as e:
            print(f"Spotify auth failed: {e}")
            self._keep_alive = False
            return False
            
    def start_ytm_auth(self) -> str:
        """Start YouTube Music authentication process"""
        if not self.driver:
            self._setup_driver()
            
        # Set flag to keep browser alive during auth process
        self._keep_alive = True
            
        # Navigate to Google login
        self.driver.get("https://accounts.google.com/signin")
        
        # Wait for login form
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "identifier"))
        )
        
        return self.driver.current_url
        
    def complete_ytm_auth(self) -> bool:
        """Complete YouTube Music authentication and extract cookies"""
        try:
            print("Waiting for YouTube Music authentication to complete...")
            
            # Wait for successful login and navigate to YTM
            WebDriverWait(self.driver, 30).until(
                lambda driver: any(pattern in driver.current_url for pattern in [
                    "myaccount.google.com",
                    "youtube.com",
                    "music.youtube.com",
                    "accounts.google.com/ServiceLogin"
                ])
            )
            
            print(f"YouTube Music authentication successful. Current URL: {self.driver.current_url}")
            
            # Navigate to YouTube Music to get YTM-specific cookies
            self.driver.get("https://music.youtube.com")
            time.sleep(3)
            
            # Extract cookies
            self.ytm_cookies = self.driver.get_cookies()
            print(f"Extracted {len(self.ytm_cookies)} YouTube Music cookies")
            
            # Save cookies to file for later use
            with open("ytm_cookies.json", "w") as f:
                json.dump(self.ytm_cookies, f)
            
            # Don't close the browser yet - let the status checking handle it
            # self._keep_alive = False
            # self.close_driver()
                
            return True
            
        except Exception as e:
            print(f"YTM auth failed: {e}")
            self._keep_alive = False
            return False
            
    def get_spotify_cookies(self) -> Optional[Dict]:
        """Get stored Spotify cookies"""
        if self.spotify_cookies:
            return self.spotify_cookies
            
        # Try to load from file
        if os.path.exists("spotify_cookies.json"):
            with open("spotify_cookies.json", "r") as f:
                self.spotify_cookies = json.load(f)
            return self.spotify_cookies
            
        return None
        
    def get_ytm_cookies(self) -> Optional[Dict]:
        """Get stored YTM cookies"""
        if self.ytm_cookies:
            return self.ytm_cookies
            
        # Try to load from file
        if os.path.exists("ytm_cookies.json"):
            with open("ytm_cookies.json", "r") as f:
                self.ytm_cookies = json.load(f)
            return self.ytm_cookies
            
        return None
        
    def close_driver(self):
        """Close the browser driver"""
        if self.driver and not self._keep_alive:
            self.driver.quit()
            self.driver = None
            
    def force_close_driver(self):
        """Force close the browser driver regardless of keep_alive flag"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self._keep_alive = False
            
    def complete_and_close(self):
        """Complete authentication and close browser - called from API"""
        if self.driver:
            # Extract cookies if not already done
            if not self.spotify_cookies and not self.ytm_cookies:
                try:
                    current_url = self.driver.current_url
                    if "spotify.com" in current_url:
                        self.spotify_cookies = self.driver.get_cookies()
                        with open("spotify_cookies.json", "w") as f:
                            json.dump(self.spotify_cookies, f)
                    elif "youtube.com" in current_url or "google.com" in current_url:
                        self.ytm_cookies = self.driver.get_cookies()
                        with open("ytm_cookies.json", "w") as f:
                            json.dump(self.ytm_cookies, f)
                except Exception as e:
                    print(f"Error extracting cookies: {e}")
            
            # Close the browser
            self.force_close_driver()
            
    def __del__(self):
        """Cleanup on deletion - only close if not in auth process"""
        if not self._keep_alive:
            self.close_driver() 