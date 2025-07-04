from ytmusicapi import YTMusic
import json
import time
from typing import Dict, List, Optional
from auth_browser import AuthManager

class YTMFetcher:
    def __init__(self):
        self.ytm = None
        self.auth_manager = AuthManager()
        
    def _setup_ytm(self):
        """Setup YTMusic with authentication"""
        try:
            # Try to load existing auth
            self.ytm = YTMusic()
            
            # If no auth exists, we'll need to set it up
            if not self.ytm.is_authenticated():
                # This would require manual setup or browser automation
                # For now, we'll use a simplified approach
                pass
                
        except Exception as e:
            print(f"Error setting up YTMusic: {e}")
            # Fallback to unauthenticated mode
            self.ytm = YTMusic()
            
    def get_library(self) -> Dict:
        """Fetch user's YouTube Music library"""
        self._setup_ytm()
        
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
            
            # Fetch saved albums
            library["albums"] = self._fetch_saved_albums()
            
            # Fetch subscribed artists
            library["artists"] = self._fetch_subscribed_artists()
            
        except Exception as e:
            print(f"Error fetching YTM library: {e}")
            
        return library
        
    def _fetch_liked_songs(self) -> Dict:
        """Fetch user's liked songs"""
        liked_songs = {}
        
        try:
            # Get liked songs
            liked = self.ytm.get_liked_songs(limit=1000)
            
            for i, track in enumerate(liked['tracks']):
                track_id = f"liked_{i}"
                liked_songs[track_id] = {
                    "title": track.get('title', ''),
                    "artist": track.get('artists', [{}])[0].get('name', '') if track.get('artists') else '',
                    "type": "liked_song",
                    "id": track_id,
                    "ytm_id": track.get('videoId', '')
                }
                
        except Exception as e:
            print(f"Error fetching liked songs: {e}")
            
        return liked_songs
        
    def _fetch_playlists(self) -> Dict:
        """Fetch user's playlists"""
        playlists = {}
        
        try:
            # Get user playlists
            user_playlists = self.ytm.get_library_playlists()
            
            for i, playlist in enumerate(user_playlists):
                playlist_id = f"playlist_{i}"
                
                # Get tracks for this playlist
                try:
                    playlist_tracks = self.ytm.get_playlist(playlist.get('playlistId', ''), limit=1000)
                    tracks = []
                    
                    for track in playlist_tracks.get('tracks', []):
                        tracks.append({
                            "title": track.get('title', ''),
                            "artist": track.get('artists', [{}])[0].get('name', '') if track.get('artists') else '',
                            "id": track.get('videoId', ''),
                            "ytm_id": track.get('videoId', '')
                        })
                        
                except Exception as e:
                    print(f"Error fetching tracks for playlist {playlist.get('name', '')}: {e}")
                    tracks = []
                
                playlists[playlist_id] = {
                    "name": playlist.get('name', ''),
                    "type": "playlist",
                    "id": playlist_id,
                    "ytm_id": playlist.get('playlistId', ''),
                    "tracks": tracks
                }
                
        except Exception as e:
            print(f"Error fetching playlists: {e}")
            
        return playlists
        
    def _fetch_saved_albums(self) -> Dict:
        """Fetch saved albums"""
        albums = {}
        
        try:
            # Get saved albums
            saved_albums = self.ytm.get_library_albums()
            
            for i, album in enumerate(saved_albums):
                album_id = f"album_{i}"
                albums[album_id] = {
                    "name": album.get('title', ''),
                    "artist": album.get('artists', [{}])[0].get('name', '') if album.get('artists') else '',
                    "type": "album",
                    "id": album_id,
                    "ytm_id": album.get('browseId', '')
                }
                
        except Exception as e:
            print(f"Error fetching saved albums: {e}")
            
        return albums
        
    def _fetch_subscribed_artists(self) -> Dict:
        """Fetch subscribed artists"""
        artists = {}
        
        try:
            # Get subscribed artists
            subscribed_artists = self.ytm.get_library_subscriptions()
            
            for i, artist in enumerate(subscribed_artists):
                artist_id = f"artist_{i}"
                artists[artist_id] = {
                    "name": artist.get('artist', ''),
                    "type": "artist",
                    "id": artist_id,
                    "ytm_id": artist.get('browseId', '')
                }
                
        except Exception as e:
            print(f"Error fetching subscribed artists: {e}")
            
        return artists
        
    def search_track(self, title: str, artist: str) -> Optional[Dict]:
        """Search for a track on YouTube Music"""
        try:
            search_query = f"{title} {artist}"
            results = self.ytm.search(search_query, filter="songs", limit=5)
            
            if results:
                # Return the first result
                track = results[0]
                return {
                    "title": track.get('title', ''),
                    "artist": track.get('artists', [{}])[0].get('name', '') if track.get('artists') else '',
                    "ytm_id": track.get('videoId', ''),
                    "confidence": 0.8  # Placeholder confidence score
                }
                
        except Exception as e:
            print(f"Error searching for track '{title}' by '{artist}': {e}")
            
        return None
        
    def create_playlist(self, playlist_data: Dict) -> str:
        """Create a new playlist on YouTube Music"""
        try:
            # Create playlist
            playlist_name = playlist_data.get("name", "Converted Playlist")
            playlist_id = self.ytm.create_playlist(playlist_name, "Playlist converted from another platform")
            
            # Add tracks to playlist
            track_ids = []
            for track in playlist_data.get("tracks", []):
                if track.get("ytm_id"):
                    track_ids.append(track["ytm_id"])
                    
            if track_ids:
                self.ytm.add_playlist_items(playlist_id, track_ids)
                
            # Return playlist URL
            return f"https://music.youtube.com/playlist?list={playlist_id}"
            
        except Exception as e:
            print(f"Error creating YTM playlist: {e}")
            return ""
            
    def get_playlist_url(self, playlist_id: str) -> str:
        """Get URL for a playlist"""
        return f"https://music.youtube.com/playlist?list={playlist_id}"
        
    def get_track_url(self, track_id: str) -> str:
        """Get URL for a track"""
        return f"https://music.youtube.com/watch?v={track_id}" 