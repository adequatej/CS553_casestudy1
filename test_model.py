import pytest
from unittest.mock import patch
from app import spotify_rec

# Mocking the Spotify API calls
@patch("spotipy.Spotify.search")
@patch("spotipy.Spotify.recommendations")
def test_spotify_rec(mock_recommendations, mock_search):
    # Define mock search result
    mock_search.return_value = {
        'tracks': {
            'items': [{'uri': 'spotify:track:123', 'name': 'Shape of You', 'artists': [{'name': 'Ed Sheeran'}]}]
        }
    }

    # Define mock recommendations result
    mock_recommendations.return_value = {
        'tracks': [
            {'name': 'Song 1', 'artists': [{'name': 'Artist 1'}]},
            {'name': 'Song 2', 'artists': [{'name': 'Artist 2'}]}
        ]
    }

    # Call the function
    result = spotify_rec("Shape of You", "Ed Sheeran", "your_client_id", "your_client_secret")

    # Check that the result is not empty and is a string
    assert isinstance(result, str)
    assert len(result) > 0

    # Assert that the result contains the expected recommendations
    assert "Song 1 by Artist 1" in result
    assert "Song 2 by Artist 2" in result
