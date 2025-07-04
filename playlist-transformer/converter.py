from typing import Dict, List
import json

class Converter:
    def __init__(self):
        self.platform_formats = {
            "spotify": {
                "track_id_prefix": "spotify:track:",
                "playlist_id_prefix": "spotify:playlist:",
                "url_base": "https://open.spotify.com"
            },
            "ytm": {
                "track_id_prefix": "",
                "playlist_id_prefix": "",
                "url_base": "https://music.youtube.com"
            }
        }
        
    def create_playlist_data(self, matched_tracks: List[Dict], target_platform: str) -> Dict:
        """Create playlist data for the target platform"""
        playlist_data = {
            "name": f"Converted Playlist ({len(matched_tracks)} tracks)",
            "description": "Playlist converted from another platform",
            "tracks": [],
            "platform": target_platform
        }
        
        for track in matched_tracks:
            if track.get("status") in ["matched", "low_confidence"]:
                converted_track = self._convert_track_format(track, target_platform)
                if converted_track:
                    playlist_data["tracks"].append(converted_track)
                    
        return playlist_data
        
    def _convert_track_format(self, track: Dict, target_platform: str) -> Dict:
        """Convert track data to target platform format"""
        if target_platform == "spotify":
            return self._to_spotify_format(track)
        else:  # ytm
            return self._to_ytm_format(track)
            
    def _to_spotify_format(self, track: Dict) -> Dict:
        """Convert track to Spotify format"""
        return {
            "id": track.get("matched_id", ""),
            "title": track.get("matched_title", track.get("original_title", "")),
            "artist": track.get("matched_artist", track.get("original_artist", "")),
            "spotify_id": track.get("matched_id", ""),
            "url": f"https://open.spotify.com/track/{track.get('matched_id', '')}" if track.get("matched_id") else ""
        }
        
    def _to_ytm_format(self, track: Dict) -> Dict:
        """Convert track to YouTube Music format"""
        return {
            "id": track.get("matched_id", ""),
            "title": track.get("matched_title", track.get("original_title", "")),
            "artist": track.get("matched_artist", track.get("original_artist", "")),
            "ytm_id": track.get("matched_id", ""),
            "url": f"https://music.youtube.com/watch?v={track.get('matched_id', '')}" if track.get("matched_id") else ""
        }
        
    def normalize_track_data(self, track: Dict, source_platform: str) -> Dict:
        """Normalize track data to common format"""
        normalized = {
            "title": "",
            "artist": "",
            "album": "",
            "duration": 0,
            "id": "",
            "source_platform": source_platform
        }
        
        if source_platform == "spotify":
            normalized.update({
                "title": track.get("title", ""),
                "artist": track.get("artist", ""),
                "album": track.get("album", ""),
                "duration": track.get("duration_ms", 0),
                "id": track.get("id", "")
            })
        elif source_platform == "ytm":
            normalized.update({
                "title": track.get("title", ""),
                "artist": track.get("artist", ""),
                "album": track.get("album", ""),
                "duration": track.get("duration", 0),
                "id": track.get("videoId", "")
            })
            
        return normalized
        
    def create_playlist_metadata(self, name: str, description: str, track_count: int, source_platform: str) -> Dict:
        """Create playlist metadata"""
        return {
            "name": name,
            "description": description,
            "track_count": track_count,
            "source_platform": source_platform,
            "created_at": "2024-01-01T00:00:00Z"  # Placeholder
        } 