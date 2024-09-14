import gradio as gr
from huggingface_hub import InferenceClient
import torch
from transformers import pipeline
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Inference client setup
client = InferenceClient("HuggingFaceH4/zephyr-7b-beta")
pipe = pipeline("text-generation", "microsoft/Phi-3-mini-4k-instruct", torch_dtype=torch.bfloat16, device_map="auto")

# Function to get Spotify recommendations
def spotify_rec(track_name, artist, client_id, client_secret):
    # Validate client ID and client secret
    if not client_id or not client_secret:
        return "Please provide Spotify API credentials."

    # Set up Spotify credentials
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # Get track URI
    results = sp.search(q=f"track:{track_name} artist:{artist}", type='track')
    if not results['tracks']['items']:
        return "No recommendations found for the given track name and artist."
    
    track_uri = results['tracks']['items'][0]['uri']

    # Get recommended tracks
    recommendations = sp.recommendations(seed_tracks=[track_uri])['tracks']
    
    if not recommendations:
        return "No recommendations found."
    
    recommendation_list = [f"{track['name']} by {track['artists'][0]['name']}" for track in recommendations]
    return "\n".join(recommendation_list)

# Global flag to handle cancellation
stop_inference = False

def respond(
    track_name,
    artist,
    history: list[tuple[str, str]],
    system_message="You are a music expert chatbot that provides song recommendations based on user emotions.",
    max_tokens=512,
    use_local_model=False,
    client_id=None,
    client_secret=None
):

    global stop_inference
    stop_inference = False  # Reset cancellation flag

    # Initialize history if it's None
    if history is None:
        history = []

    # Get Spotify Recs based on the user's input
    recommendations = spotify_rec(track_name, artist, client_id, client_secret)
    response += "\n" + recommendations    

    if use_local_model:
        # local inference 
        messages = [{"role": "system", "content": system_message}]
        for val in history:
            if val[0]:
                messages.append({"role": "user", "content": val[0]})
            if val[1]:
                messages.append({"role": "assistant", "content": val[1]})
        messages.append({"role": "user", "content": message})

        response = ""
        for output in pipe(
            messages,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            top_p=top_p,
        ):
            if stop_inference:
                response = "Inference cancelled."
                yield history + [(message, response)]
                return
            token = output['generated_text'][-1]['content']
            response += token
            yield history + [(message, response)]  # Yield history + new response

    else:
        # API-based inference 
        messages = [{"role": "system", "content": system_message}]
        for val in history:
            if val[0]:
                messages.append({"role": "user", "content": val[0]})
            if val[1]:
                messages.append({"role": "assistant", "content": val[1]})
        messages.append({"role": "user", "content": message})

        response = ""
        for message_chunk in client.chat_completion(
            messages,
            max_tokens=max_tokens,
            stream=True,
            temperature=temperature,
            top_p=top_p,
        ):
            if stop_inference:
                response = "Inference cancelled."
                yield history + [(message, response)]
                return
            if stop_inference:
                response = "Inference cancelled."
                break
            token = message_chunk.choices[0].delta.content
            response += token
            yield history + [(message, response)]  # Yield history + new response


def cancel_inference():
    global stop_inference
    stop_inference = True

# Custom CSS for a fancy look
custom_css = """
#main-container {
    background-color: #f0f0f0;
    font-family: 'Times New Roman', sans-serif;
}

.gradio-container {
    max-width: 700px;
    margin: 0 auto;
    padding: 20px;
    background: black;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    border-radius: 10px;
}

.gr-button {
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.gr-button:hover {
    background-color: #0056b3;
}

.gr-slider input {
    color: #4CAF50;
}

.gr-chat {
    font-size: 16px;
}

#title {
    text-align: center;
    font-size: 2.5em;
    margin-bottom: 20px;
    color: #333;
}
"""

# Define the interface
with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("<h1 style='text-align: center;'>🎶 Emotion-Based Song Recommendation Bot 🎶</h1>")
    gr.Markdown("Interact with the AI chatbot using customizable settings below.")

    with gr.Row():
        system_message = gr.Textbox(value="You are a music expert chatbot that provides song recommendations based on user emotions", label="System message", interactive=True)
        use_local_model = gr.Checkbox(label="Use Local Model", value=False)

    with gr.Row():
        max_tokens = gr.Slider(minimum=1, maximum=2048, value=512, step=1, label="Max new tokens")

    chat_history = gr.Chatbot(label="Chat")

    # New input fields for track name, artist, client ID, and client secret
    track_name = gr.Textbox(show_label=False, placeholder="Enter a song name:")
    artist = gr.Textbox(show_label=False, placeholder="Enter the artist:")
    
    client_id = gr.Textbox(show_label=False, placeholder="Spotify Client ID:")
    client_secret = gr.Textbox(show_label=False, placeholder="Spotify Client Secret:", type="password")

    cancel_button = gr.Button("Cancel Inference", variant="danger")

    # Adjusted to ensure history is maintained and passed correctly
    track_name.submit(respond, [track_name, artist, chat_history, system_message, max_tokens, use_local_model, client_id, client_secret], chat_history)
    
    artist.submit(respond, [track_name, artist, chat_history, system_message, max_tokens, use_local_model, client_id, client_secret], chat_history)

    cancel_button.click(cancel_inference)

if __name__ == "__main__":
    demo.launch(share=False)  # Remove share=True because it's not supported on HF Spaces



