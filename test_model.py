import pytest

def test_suggest_song():
    assert suggest_song("happy") == "You might enjoy 'Happy' by Pharrell Williams."
    assert suggest_song("sad") == "You might enjoy 'Someone Like You' by Adele."
    assert suggest_song("angry") == "Listen to 'Killing in the Name' by Rage Against the Machine."
    assert suggest_song("neutral") == "Tell me more about your mood!"

