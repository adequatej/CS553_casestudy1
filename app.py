import gradio as gr
from huggingface_hub import InferenceClient
import torch
from transformers import pipeline

# Inference client setup
client = InferenceClient("HuggingFaceH4/zephyr-7b-beta")
pipe = pipeline("text-generation", "microsoft/Phi-3-mini-4k-instruct", torch_dtype=torch.bfloat16, device_map="auto")

# Global flag to handle cancellation
stop_inference = False


# For emotion suggestion
def suggest_song(message):
    """Provide song recommendations based on user feelings."""
    if "happy" in message.lower():
        return "How about listening to 'Happy' by Pharrell Williams?"
    elif "sad" in message.lower():
        return "You might enjoy 'Someone Like You' by Adele."
    else:
        return "Tell me more about your mood!"


def respond(
    message,
    history: list[tuple[str, str]],
    system_message="You are a music expert chatbot that provides song recommendations based on user emotions.",
    max_tokens=512,
    top_p=0.95,
    use_local_model=False,
):

    global stop_inference
    stop_inference = False  # Reset cancellation flag

    # Initialize history if it's None
    if history is None:
        history = []

    # Emotion detection logic
    emotion_response = suggest_song(message)
    response += "\n" + emotion_response # Append emotion-based song recommendation

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
        top_p = gr.Slider(minimum=0.1, maximum=1.0, value=0.95, step=0.05, label="Top-p (nucleus sampling)")

    chat_history = gr.Chatbot(label="Chat")

    user_input = gr.Textbox(show_label=False, placeholder="How are you feeling?:")

    cancel_button = gr.Button("Cancel Inference", variant="danger")

    # Adjusted to ensure history is maintained and passed correctly
    user_input.submit(respond, [user_input, chat_history, system_message, max_tokens, top_p, use_local_model], chat_history)

    cancel_button.click(cancel_inference)

if __name__ == "__main__":
    demo.launch(share=False)  # Remove share=True because it's not supported on HF Spaces

