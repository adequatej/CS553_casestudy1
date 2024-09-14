# test_app.py
import pytest
from app import spotify_rec  # Import the function to be tested

def test_spotify_rec():
    # Define your test input
    track_name = "Shape of You"
    artist = "Ed Sheeran"
    client_id = "your_client_id"
    client_secret = "your_client_secret"

    # Call the function
    result = spotify_rec(track_name, artist, client_id, client_secret)

    # Check that the result is not empty and is a string
    assert isinstance(result, str)
    assert len(result) > 0
