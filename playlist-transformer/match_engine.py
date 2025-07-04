from thefuzz import fuzz
from typing import Dict, List, Optional
from fetch_spotify import SpotifyFetcher
from fetch_ytm import YTMFetcher

class MatchEngine:
    def __init__(self):
        self.spotify_fetcher = SpotifyFetcher()
        self.ytm_fetcher = YTMFetcher()
        self.confidence_threshold = 70
        
    def match_tracks(self, tracks: List[Dict], source_platform: str, target_platform: str) -> List[Dict]:
        """Match tracks from source platform to target platform"""
        matched_tracks = []
        
        for track in tracks:
            match_result = self._match_single_track(track, target_platform)
            if match_result:
                matched_tracks.append({
                    "original_id": track.get("id", ""),
                    "original_title": track.get("title", ""),
                    "original_artist": track.get("artist", ""),
                    "matched_title": match_result.get("title", ""),
                    "matched_artist": match_result.get("artist", ""),
                    "matched_id": match_result.get("id", ""),
                    "confidence": match_result.get("confidence", 0),
                    "status": "matched" if match_result.get("confidence", 0) >= self.confidence_threshold else "low_confidence"
                })
            else:
                matched_tracks.append({
                    "original_id": track.get("id", ""),
                    "original_title": track.get("title", ""),
                    "original_artist": track.get("artist", ""),
                    "matched_title": "",
                    "matched_artist": "",
                    "matched_id": "",
                    "confidence": 0,
                    "status": "not_found"
                })
                
        return matched_tracks
        
    def _match_single_track(self, track: Dict, target_platform: str) -> Optional[Dict]:
        """Match a single track to the target platform"""
        title = track.get("title", "")
        artist = track.get("artist", "")
        
        if target_platform == "spotify":
            return self._search_spotify(title, artist)
        else:  # ytm
            return self._search_ytm(title, artist)
            
    def _search_spotify(self, title: str, artist: str) -> Optional[Dict]:
        """Search for track on Spotify"""
        # This would use Spotify's search API
        # For now, return a placeholder with fuzzy matching
        search_query = f"{title} {artist}"
        
        # Simulate search results with fuzzy matching
        potential_matches = [
            {"title": title, "artist": artist, "id": f"spotify_{title}_{artist}"},
            {"title": title + " (Remix)", "artist": artist, "id": f"spotify_{title}_remix"},
            {"title": title, "artist": artist + " feat. Someone", "id": f"spotify_{title}_feat"}
        ]
        
        best_match = None
        best_score = 0
        
        for match in potential_matches:
            title_score = fuzz.ratio(title.lower(), match["title"].lower())
            artist_score = fuzz.ratio(artist.lower(), match["artist"].lower())
            combined_score = (title_score + artist_score) / 2
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = match
                
        if best_match and best_score >= self.confidence_threshold:
            return {
                "title": best_match["title"],
                "artist": best_match["artist"],
                "id": best_match["id"],
                "confidence": best_score
            }
            
        return None
        
    def _search_ytm(self, title: str, artist: str) -> Optional[Dict]:
        """Search for track on YouTube Music"""
        try:
            result = self.ytm_fetcher.search_track(title, artist)
            if result:
                # Calculate confidence using fuzzy matching
                title_score = fuzz.ratio(title.lower(), result["title"].lower())
                artist_score = fuzz.ratio(artist.lower(), result["artist"].lower())
                combined_score = (title_score + artist_score) / 2
                
                result["confidence"] = combined_score
                return result
        except Exception as e:
            print(f"Error searching YTM: {e}")
            
        return None
        
    def rematch_track(self, title: str, artist: str, target_platform: str) -> Dict:
        """Re-match a track with corrected information"""
        if target_platform == "spotify":
            result = self._search_spotify(title, artist)
        else:
            result = self._search_ytm(title, artist)
            
        if result:
            return {
                "matched_title": result["title"],
                "matched_artist": result["artist"],
                "matched_id": result["id"],
                "confidence": result["confidence"],
                "status": "matched" if result["confidence"] >= self.confidence_threshold else "low_confidence"
            }
        else:
            return {
                "matched_title": "",
                "matched_artist": "",
                "matched_id": "",
                "confidence": 0,
                "status": "not_found"
            }
            
    def batch_match(self, tracks: List[Dict], target_platform: str) -> List[Dict]:
        """Batch match multiple tracks for efficiency"""
        # This could implement batch searching if the APIs support it
        return self.match_tracks(tracks, "unknown", target_platform) 