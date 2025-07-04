from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import os
import asyncio
import signal
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Import our modules
from auth_browser import AuthManager
from fetch_spotify import SpotifyFetcher
from fetch_ytm import YTMFetcher
from match_engine import MatchEngine
from converter import Converter

# Define missing types for type hinting
class AuthProvider:
    """Base class for authentication providers"""
    pass

class AuthResult:
    """Result of authentication attempt"""
    pass

class Session:
    """Session management class"""
    pass

app = FastAPI(title="Spotify ↔ YouTube Music Converter")

# Templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global state (in production, use proper session management)
session_data = {}

# Initialize cookie files if they don't exist
try:
    if not os.path.exists("spotify_cookies.json"):
        with open("spotify_cookies.json", "w") as f:
            json.dump([], f)
    if not os.path.exists("ytm_cookies.json"):
        with open("ytm_cookies.json", "w") as f:
            json.dump([], f)
except Exception as e:
    print(f"Warning: Could not initialize cookie files: {e}")

@dataclass
class ConversionSession:
    source_platform: str
    target_platform: str
    source_library: Dict = None
    matched_tracks: List[Dict] = None
    selected_tracks: List[str] = None
    auth_manager: Optional[AuthManager] = None  # Store auth manager instance
    source_authenticated: bool = False  # Track source platform auth status
    target_authenticated: bool = False  # Track target platform auth status

# Extract platform-specific logic
class SpotifyAuthProvider(AuthProvider):
    def authenticate(self) -> AuthResult:
        # Placeholder implementation
        pass

class YTMAuthProvider(AuthProvider):
    def authenticate(self) -> AuthResult:
        # Placeholder implementation
        pass

# Separate concerns
class SessionManager:
    def create_session(self) -> Session:
        # Placeholder implementation
        pass
    
    def validate_session(self, session_id: str) -> bool:
        # Placeholder implementation
        return False

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Landing page to choose conversion direction"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/auth/start")
async def start_auth(source: str = Form(...), target: str = Form(...)):
    """Initialize authentication for both platforms"""
    session_id = f"session_{len(session_data)}"
    
    # Create auth manager and store it in session
    auth_manager = AuthManager()
    session_data[session_id] = ConversionSession(
        source, target, 
        auth_manager=auth_manager,
        source_authenticated=False,
        target_authenticated=False
    )
    
    # Start auth for source platform first
    if source == "spotify":
        auth_url = auth_manager.start_spotify_auth()
    else:  # ytm
        auth_url = auth_manager.start_ytm_auth()
    
    # Redirect to the authentication page instead of returning JSON
    return RedirectResponse(url=f"/auth/{source}?session_id={session_id}")

@app.get("/auth/{platform}")
@app.post("/auth/{platform}")
async def auth_page(request: Request, platform: str, session_id: str):
    """Auth page for specific platform"""
    if session_id not in session_data:
        raise HTTPException(status_code=400, detail="Invalid session")
    
    session = session_data[session_id]
    
    # Determine if this is source or target platform
    is_source = platform == session.source_platform
    is_target = platform == session.target_platform
    
    if not is_source and not is_target:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    return templates.TemplateResponse(
        "auth.html", 
        {
            "request": request, 
            "platform": platform, 
            "session_id": session_id,
            "is_source": is_source,
            "is_target": is_target
        }
    )

@app.post("/auth/complete")
async def complete_auth(session_id: str = Form(...), platform: str = Form(...)):
    """Complete authentication and fetch library"""
    print(f"DEBUG: Auth completion request received - session_id: {session_id}, platform: {platform}")
    
    if session_id not in session_data:
        print(f"DEBUG: Invalid session_id: {session_id}")
        raise HTTPException(status_code=400, detail="Invalid session")
    
    session = session_data[session_id]
    print(f"DEBUG: Session found - source: {session.source_platform}, target: {session.target_platform}")
    print(f"DEBUG: Session state - source_auth: {session.source_authenticated}, target_auth: {session.target_authenticated}")
    
    # Use the stored auth manager instance
    if not session.auth_manager:
        print(f"DEBUG: No auth manager found for session {session_id}")
        raise HTTPException(status_code=400, detail="No auth manager found")
    
    print(f"DEBUG: Completing authentication for platform {platform} in session {session_id}")
    
    try:
        # Complete auth for the platform
        if platform == "spotify":
            print(f"DEBUG: Processing Spotify authentication for session {session_id}")
            
            if platform == session.source_platform:
                # This is source platform authentication
                print(f"DEBUG: Spotify source authentication - skipping library fetch for now")
                session.source_library = {"playlists": {}, "liked_songs": {}, "albums": {}, "artists": {}}
                session.source_authenticated = True
                print(f"DEBUG: Spotify source authentication marked as complete")
            else:
                # This is target platform authentication
                print(f"DEBUG: Spotify target authentication successful for session {session_id}")
                session.target_authenticated = True
        else:  # ytm
            print(f"DEBUG: Processing YTM authentication for session {session_id}")
            
            if platform == session.source_platform:
                # This is source platform authentication
                print(f"DEBUG: YTM source authentication - skipping library fetch for now")
                session.source_library = {"playlists": {}, "liked_songs": {}, "albums": {}, "artists": {}}
                session.source_authenticated = True
                print(f"DEBUG: YTM source authentication marked as complete")
            else:
                # This is target platform authentication
                print(f"DEBUG: YTM target authentication successful for session {session_id}")
                session.target_authenticated = True
        
        print(f"DEBUG: Authentication successful, closing browser...")
        # Close the browser after successful authentication
        if session.auth_manager:
            session.auth_manager.complete_and_close()
            session.auth_manager = None
            print(f"DEBUG: Browser closed, auth_manager set to None")
        
        # Check if we need to authenticate the target platform
        if session.source_authenticated and not session.target_authenticated:
            print(f"DEBUG: Starting target platform authentication for session {session_id}")
            # Create new auth manager for target platform
            auth_manager = AuthManager()
            session.auth_manager = auth_manager
            
            # Start authentication for target platform
            if session.target_platform == "spotify":
                print(f"DEBUG: Starting Spotify target authentication")
                auth_url = auth_manager.start_spotify_auth()
            else:  # ytm
                print(f"DEBUG: Starting YTM target authentication")
                auth_url = auth_manager.start_ytm_auth()
            
            print(f"DEBUG: Redirecting to {session.target_platform} authentication")
            # Redirect to target platform authentication
            return RedirectResponse(url=f"/auth/{session.target_platform}?session_id={session_id}")
        
        # Both platforms authenticated, go to library
        print(f"DEBUG: All authentication completed for session {session_id}, redirecting to library")
        return RedirectResponse(url=f"/library?session_id={session_id}")
        
    except Exception as e:
        print(f"DEBUG: Exception in auth completion: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Authentication completion failed: {str(e)}")

@app.post("/auth/cancel")
async def cancel_auth(session_id: str = Form(...)):
    """Cancel authentication and cleanup browser"""
    if session_id not in session_data:
        raise HTTPException(status_code=400, detail="Invalid session")
    
    session = session_data[session_id]
    
    # Clean up auth manager if it exists
    if session.auth_manager:
        session.auth_manager.force_close_driver()
        session.auth_manager = None
    
    # Remove session
    del session_data[session_id]
    
    return RedirectResponse(url="/")

@app.get("/auth/status/{session_id}")
async def check_auth_status(session_id: str):
    """Check authentication status for a session"""
    if session_id not in session_data:
        raise HTTPException(status_code=400, detail="Invalid session")
    
    session = session_data[session_id]
    
    if not session.auth_manager:
        print(f"DEBUG: No auth manager for session {session_id}")
        return {"status": "completed", "message": "Authentication completed"}
    
    # Check if the browser is still open and user has logged in
    try:
        driver = session.auth_manager.driver
        if not driver:
            print(f"DEBUG: No driver for session {session_id}")
            return {"status": "error", "message": "Browser window closed"}
        
        current_url = driver.current_url
        print(f"DEBUG: Current URL for session {session_id}: {current_url}")
        
        # Determine which platform we're currently authenticating
        current_platform = None
        if not session.source_authenticated:
            current_platform = session.source_platform
        elif not session.target_authenticated:
            current_platform = session.target_platform
        
        if not current_platform:
            print(f"DEBUG: No current platform for session {session_id}")
            return {"status": "completed", "message": "All authentication completed"}
        
        print(f"DEBUG: Checking {current_platform} authentication for session {session_id}")
        
        # Check for successful authentication indicators
        if current_platform == "spotify":
            # Check for various Spotify authentication success patterns
            spotify_success_patterns = [
                "open.spotify.com",
                "accounts.spotify.com/authorize", 
                "spotify.com/authorize",
                "spotify.com/login",
                "spotify.com/account",
                "spotify.com/dashboard",
                "accounts.spotify.com/en/status",  # Status page after authentication
                "accounts.spotify.com/status",     # Alternative status page
                "challenge.spotify.com"            # Challenge pages (email verification, etc.)
            ]
            
            if any(pattern in current_url for pattern in spotify_success_patterns):
                platform_name = "Spotify" if current_platform == session.source_platform else "Spotify (Target)"
                print(f"DEBUG: Spotify authentication successful for session {session_id}")
                return {"status": "completed", "message": f"{platform_name} authentication successful"}
        else:  # ytm
            # Check for various YouTube Music authentication success patterns
            ytm_success_patterns = [
                "myaccount.google.com",
                "youtube.com",
                "music.youtube.com", 
                "accounts.google.com/ServiceLogin",
                "google.com/accounts"
            ]
            
            if any(pattern in current_url for pattern in ytm_success_patterns):
                platform_name = "YouTube Music" if current_platform == session.source_platform else "YouTube Music (Target)"
                print(f"DEBUG: YouTube Music authentication successful for session {session_id}")
                return {"status": "completed", "message": f"{platform_name} authentication successful"}
        
        print(f"DEBUG: Still waiting for {current_platform} authentication for session {session_id}")
        return {"status": "pending", "message": f"Waiting for {current_platform.upper()} authentication"}
        
    except Exception as e:
        print(f"DEBUG: Error checking status for session {session_id}: {e}")
        return {"status": "error", "message": f"Error checking status: {str(e)}"}

@app.get("/library")
async def show_library(request: Request, session_id: str):
    """Display user's library for selection"""
    if session_id not in session_data:
        raise HTTPException(status_code=400, detail="Invalid session")
    
    session = session_data[session_id]
    if not session.source_library:
        raise HTTPException(status_code=400, detail="No library data")
    
    return templates.TemplateResponse(
        "library.html",
        {
            "request": request,
            "session_id": session_id,
            "library": session.source_library,
            "platform": session.source_platform,
            "target_platform": session.target_platform
        }
    )

@app.post("/match")
async def start_matching(session_id: str = Form(...), selected_items: List[str] = Form(...)):
    """Start matching selected items on target platform"""
    if session_id not in session_data:
        raise HTTPException(status_code=400, detail="Invalid session")
    
    session = session_data[session_id]
    session.selected_tracks = selected_items
    
    # Get selected tracks from library
    tracks_to_match = []
    for item_id in selected_items:
        if item_id in session.source_library.get("tracks", {}):
            tracks_to_match.append(session.source_library["tracks"][item_id])
    
    # Perform matching
    match_engine = MatchEngine()
    session.matched_tracks = match_engine.match_tracks(
        tracks_to_match, 
        session.source_platform, 
        session.target_platform
    )
    
    return RedirectResponse(url=f"/match/results?session_id={session_id}")

@app.get("/match/results")
async def show_matches(request: Request, session_id: str):
    """Show matching results with correction options"""
    if session_id not in session_data:
        raise HTTPException(status_code=400, detail="Invalid session")
    
    session = session_data[session_id]
    if not session.matched_tracks:
        raise HTTPException(status_code=400, detail="No matches found")
    
    return templates.TemplateResponse(
        "matches.html",
        {
            "request": request,
            "session_id": session_id,
            "matches": session.matched_tracks,
            "target_platform": session.target_platform
        }
    )

@app.post("/match/correct")
async def correct_match(
    session_id: str = Form(...),
    track_id: str = Form(...),
    corrected_title: str = Form(...),
    corrected_artist: str = Form(...)
):
    """Correct a mismatched track"""
    if session_id not in session_data:
        raise HTTPException(status_code=400, detail="Invalid session")
    
    session = session_data[session_id]
    match_engine = MatchEngine()
    
    # Re-match with corrected info
    corrected_match = match_engine.rematch_track(
        corrected_title, 
        corrected_artist, 
        session.target_platform
    )
    
    # Update the match in session
    for match in session.matched_tracks:
        if match["original_id"] == track_id:
            match.update(corrected_match)
            break
    
    return {"success": True, "match": corrected_match}

@app.post("/confirm")
async def confirm_conversion(
    session_id: str = Form(...),
    final_tracks: List[str] = Form(...)
):
    """Create playlist on target platform"""
    if session_id not in session_data:
        raise HTTPException(status_code=400, detail="Invalid session")
    
    session = session_data[session_id]
    
    # Filter to only selected tracks
    final_matches = [
        match for match in session.matched_tracks 
        if match["original_id"] in final_tracks
    ]
    
    # Convert and create playlist
    converter = Converter()
    playlist_data = converter.create_playlist_data(final_matches, session.target_platform)
    
    # Create playlist on target platform
    if session.target_platform == "spotify":
        fetcher = SpotifyFetcher()
        playlist_url = fetcher.create_playlist(playlist_data)
    else:  # ytm
        fetcher = YTMFetcher()
        playlist_url = fetcher.create_playlist(playlist_data)
    
    # Clean up session
    del session_data[session_id]
    
    return {
        "success": True,
        "playlist_url": playlist_url,
        "track_count": len(final_matches)
    }

@app.get("/status")
async def get_status():
    """Simple status endpoint"""
    return {
        "status": "running",
        "active_sessions": len(session_data),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000) 