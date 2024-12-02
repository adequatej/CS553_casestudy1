import gradio as gr
from huggingface_hub import InferenceClient
# import torch
# from transformers import pipeline
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from prometheus_client import Counter, Summary, Gauge

# Inference client setup
client = InferenceClient("HuggingFaceH4/zephyr-7b-beta")
#pipe = pipeline("text-generation", "microsoft/Phi-3-mini-4k-instruct", torch_dtype=torch.bfloat16, device_map="auto")

# Prometheus Metrics
RECOMMENDATIONS_PROCESSED = Counter('app_recommendations_processed', 'Total number of recommendation requests processed')
SUCCESSFUL_RECOMMENDATIONS = Counter('app_successful_recommendations', 'Total number of successful recommendations')
FAILED_RECOMMENDATIONS = Counter('app_failed_recommendations', 'Total number of failed recommendations')
RECOMMENDATION_DURATION = Summary('app_recommendation_duration_seconds', 'Time spent processing recommendation')
USER_INTERACTIONS = Counter('app_user_interactions', 'Total number of user interactions')
CANCELLED_RECOMMENDATIONS = Counter('app_cancelled_recommendations', 'Total number of cancelled recommendations')

# Prometheus Metrics
RECOMMENDATIONS_PROCESSED = Counter('app_recommendations_processed', 'Total number of recommendation requests processed')
SUCCESSFUL_RECOMMENDATIONS = Counter('app_successful_recommendations', 'Total number of successful recommendations')
FAILED_RECOMMENDATIONS = Counter('app_failed_recommendations', 'Total number of failed recommendations')
RECOMMENDATION_DURATION = Summary('app_recommendation_duration_seconds', 'Time spent processing recommendation')
USER_INTERACTIONS = Counter('app_user_interactions', 'Total number of user interactions')
CANCELLED_RECOMMENDATIONS = Counter('app_cancelled_recommendations', 'Total number of cancelled recommendations')

# Function to get Spotify recommendations
def spotify_rec(track_name, artist, client_id, client_secret):
    # Validate client ID and client secret
    if not client_id or not client_secret:
        FAILED_RECOMMENDATIONS.inc()  # Increment failed recommendations if credentials are missing
        return "Please provide Spotify API credentials."

    # Set up Spotify credentials
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # Get track 
    results = sp.search(q=f"track:{track_name} artist:{artist}", type='track')
    if not results['tracks']['items']:
        FAILED_RECOMMENDATIONS.inc()  # Increment failed recommendations if no tracks found
        return "No recommendations found for the given track name and artist."
    
    track_uri = results['tracks']['items'][0]['uri']

    # Get recommended tracks
    recommendations = sp.recommendations(seed_tracks=[track_uri])['tracks']
    
    if not recommendations:
        FAILED_RECOMMENDATIONS.inc()  # Increment failed recommendations if no recommendations found
        return "No recommendations found."
    
    recommendation_list = [f"{track['name']} by {track['artists'][0]['name']}" for track in recommendations]
    
    SUCCESSFUL_RECOMMENDATIONS.inc()  # Increment successful recommendations
    RECOMMENDATIONS_PROCESSED.inc()  # Increment total recommendations processed
    
    return "\n".join(recommendation_list)

# Global flag to handle cancellation
stop_inference = False

@RECOMMENDATION_DURATION.time()  # Track the time it takes to process recommendations
def respond(
    track_name,
    artist,
    history: list[tuple[str, str]],  # Ensure the history is a list of tuples
    system_message="You are a music expert chatbot that provides song recommendations based on user emotions.",
    max_tokens=512,
    use_local_model=False,
    client_id=None,
    client_secret=None
):
    global stop_inference
    stop_inference = False  # Reset cancellation flag
    USER_INTERACTIONS.inc()  # Track each user interaction

    # Initialize history if it's None
    if history is None:
        history = []

    response = ""  # Initialize response

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
        messages.append({"role": "user", "content": f"{track_name} by {artist}"})

        response = ""
        for output in pipe(
            messages,
            max_new_tokens=max_tokens,
            do_sample=True,
        ):
            if stop_inference:
                CANCELLED_RECOMMENDATIONS.inc()  # Increment cancelled recommendations if the user cancels
                response = "Inference cancelled."
                yield history + [(track_name, response)]
                return
            token = output['generated_text'] 
            response += token
            yield history + [(track_name, response)]  # Yield history + new response

    else:
        # API-based inference 
        messages = [{"role": "system", "content": system_message}]
        for val in history:
            if val[0]:
                messages.append({"role": "user", "content": val[0]})
            if val[1]:
                messages.append({"role": "assistant", "content": val[1]})
        messages.append({"role": "user", "content": f"{track_name} by {artist}"})

        for message_chunk in client.chat_completion(
            messages,
            max_tokens=max_tokens,
            stream=True,
        ):
            if stop_inference:
                CANCELLED_RECOMMENDATIONS.inc()  # Increment cancelled recommendations if the user cancels
                response = "Inference cancelled."
                yield history + [(track_name, response)]
                return
            token = message_chunk.choices[0].delta.content
            response += token
            yield history + [(track_name, response)]  # Yield history + new response

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

    cancel_button = gr.Button("Cancel")

    track_name.submit(respond, [track_name, artist, chat_history, system_message, max_tokens, use_local_model, client_id, client_secret], chat_history)
    artist.submit(respond, [track_name, artist, chat_history, system_message, max_tokens, use_local_model, client_id, client_secret], chat_history)

    cancel_button.click(cancel_inference)

# Expose Prometheus Metrics
from prometheus_client import start_http_server
start_http_server(8000)

# Launch Gradio app
demo.launch(share=False) #7860
