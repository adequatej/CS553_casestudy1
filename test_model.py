import pytest
from unittest.mock import patch
from app import spotify_rec

# Mocking the Spotify API calls because don't want to rely on real Spotify API responses
@patch("spotipy.Spotify.search")
@patch("spotipy.Spotify.recommendations")
def test_spotify_rec(mock_recommendations, mock_search):
    # Define search results
    mock_search.return_value = {
        'tracks': {
            'items': [{'uri': 'spotify:track:123', 'name': 'Shape of You', 'artists': [{'name': 'Ed Sheeran'}]}]
        }
    }

    # Define rec results
    mock_recommendations.return_value = {
        'tracks': [
            {'name': 'Song 1', 'artists': [{'name': 'Artist 1'}]},
            {'name': 'Song 2', 'artists': [{'name': 'Artist 2'}]}
        ]
    }

    result = spotify_rec("Shape of You", "Ed Sheeran", "your_client_id", "your_client_secret")

    # Check result
    assert isinstance(result, str)
    assert len(result) > 0

    # Assert that the result contains the expected recommendations
    assert "Song 1 by Artist 1" in result
    assert "Song 2 by Artist 2" in result
