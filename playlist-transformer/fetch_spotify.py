from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import time
from typing import Dict, List, Optional
from auth_browser import AuthManager

class SpotifyFetcher:
    def __init__(self):
        self.driver = None
        self.auth_manager = AuthManager()
        
    def _setup_driver_with_cookies(self):
        """Setup driver and load Spotify cookies"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")  # Run in background
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Load cookies
        cookies = self.auth_manager.get_spotify_cookies()
        if cookies:
            self.driver.get("https://open.spotify.com")
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
                    
    def get_library(self) -> Dict:
        """Fetch user's Spotify library including playlists, liked songs, etc."""
        self._setup_driver_with_cookies()
        
        library = {
            "playlists": {},
            "liked_songs": {},
            "albums": {},
            "artists": {},
            "tracks": {}
        }
        
        try:
            # Fetch liked songs
            library["liked_songs"] = self._fetch_liked_songs()
            
            # Fetch playlists
            library["playlists"] = self._fetch_playlists()
            
            # Fetch followed artists
            library["artists"] = self._fetch_followed_artists()
            
            # Fetch saved albums
            library["albums"] = self._fetch_saved_albums()
            
        except Exception as e:
            print(f"Error fetching Spotify library: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                
        return library
        
    def _fetch_liked_songs(self) -> Dict:
        """Fetch user's liked songs"""
        self.driver.get("https://open.spotify.com/collection/tracks")
        time.sleep(3)
        
        liked_songs = {}
        
        # Wait for tracks to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='track-row']"))
        )
        
        # Scroll to load more tracks
        self._scroll_to_load_all()
        
        # Extract track information
        track_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='track-row']")
        
        for i, element in enumerate(track_elements):
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='track-name']")
                artist_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='track-artist']")
                
                title = title_elem.text
                artist = artist_elem.text
                track_id = f"liked_{i}"
                
                liked_songs[track_id] = {
                    "title": title,
                    "artist": artist,
                    "type": "liked_song",
                    "id": track_id
                }
                
            except Exception as e:
                print(f"Error extracting track {i}: {e}")
                continue
                
        return liked_songs
        
    def _fetch_playlists(self) -> Dict:
        """Fetch user's playlists"""
        self.driver.get("https://open.spotify.com/collection/playlists")
        time.sleep(3)
        
        playlists = {}
        
        # Wait for playlists to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='playlist-card']"))
        )
        
        playlist_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='playlist-card']")
        
        for i, element in enumerate(playlist_elements):
            try:
                name_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='playlist-name']")
                name = name_elem.text
                playlist_id = f"playlist_{i}"
                
                playlists[playlist_id] = {
                    "name": name,
                    "type": "playlist",
                    "id": playlist_id,
                    "tracks": self._fetch_playlist_tracks(element)
                }
                
            except Exception as e:
                print(f"Error extracting playlist {i}: {e}")
                continue
                
        return playlists
        
    def _fetch_playlist_tracks(self, playlist_element) -> List[Dict]:
        """Fetch tracks from a specific playlist"""
        tracks = []
        
        try:
            # Click on playlist to open it
            playlist_element.click()
            time.sleep(3)
            
            # Wait for tracks to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='track-row']"))
            )
            
            track_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='track-row']")
            
            for i, element in enumerate(track_elements):
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='track-name']")
                    artist_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='track-artist']")
                    
                    tracks.append({
                        "title": title_elem.text,
                        "artist": artist_elem.text,
                        "id": f"track_{i}"
                    })
                    
                except Exception as e:
                    print(f"Error extracting playlist track {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching playlist tracks: {e}")
            
        return tracks
        
    def _fetch_followed_artists(self) -> Dict:
        """Fetch followed artists"""
        self.driver.get("https://open.spotify.com/collection/artists")
        time.sleep(3)
        
        artists = {}
        
        try:
            artist_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='artist-card']")
            
            for i, element in enumerate(artist_elements):
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='artist-name']")
                    name = name_elem.text
                    artist_id = f"artist_{i}"
                    
                    artists[artist_id] = {
                        "name": name,
                        "type": "artist",
                        "id": artist_id
                    }
                    
                except Exception as e:
                    print(f"Error extracting artist {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching artists: {e}")
            
        return artists
        
    def _fetch_saved_albums(self) -> Dict:
        """Fetch saved albums"""
        self.driver.get("https://open.spotify.com/collection/albums")
        time.sleep(3)
        
        albums = {}
        
        try:
            album_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='album-card']")
            
            for i, element in enumerate(album_elements):
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='album-name']")
                    artist_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='album-artist']")
                    
                    name = name_elem.text
                    artist = artist_elem.text
                    album_id = f"album_{i}"
                    
                    albums[album_id] = {
                        "name": name,
                        "artist": artist,
                        "type": "album",
                        "id": album_id
                    }
                    
                except Exception as e:
                    print(f"Error extracting album {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching albums: {e}")
            
        return albums
        
    def _scroll_to_load_all(self):
        """Scroll to load all content"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
    def create_playlist(self, playlist_data: Dict) -> str:
        """Create a new playlist on Spotify"""
        self._setup_driver_with_cookies()
        
        try:
            # Navigate to create playlist page
            self.driver.get("https://open.spotify.com/playlist/create")
            time.sleep(3)
            
            # Fill playlist name
            name_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='playlist']"))
            )
            name_input.clear()
            name_input.send_keys(playlist_data["name"])
            
            # Add tracks (simplified - would need more complex logic for actual track addition)
            # This is a placeholder for the actual implementation
            
            # Get the playlist URL
            playlist_url = self.driver.current_url
            
            return playlist_url
            
        except Exception as e:
            print(f"Error creating Spotify playlist: {e}")
            return ""
        finally:
            if self.driver:
                self.driver.quit() 