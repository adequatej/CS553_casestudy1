import gradio as gr
from huggingface_hub import InferenceClient
#import torch
#from transformers import pipeline
from prometheus_client import start_http_server, Counter, Summary

# Prometheus metrics
REQUEST_COUNTER = Counter('app_requests_total', 'Total number of requests')
SUCCESSFUL_REQUESTS = Counter('app_successful_requests_total', 'Total number of successful requests')
FAILED_REQUESTS = Counter('app_failed_requests_total', 'Total number of failed requests')
REQUEST_DURATION = Summary('app_request_duration_seconds', 'Time spent processing request')

# Inference client setup
client = InferenceClient("HuggingFaceH4/zephyr-7b-beta")
# pipe = pipeline("text-generation", "microsoft/Phi-3-mini-4k-instruct", torch_dtype=torch.bfloat16, device_map="auto")

# Global flag to handle cancellation
stop_inference = False

def respond(
    message,
    history: list[tuple[str, str]],
    system_message="You are a friendly Chatbot.",
    max_tokens=512,
    temperature=0.7,
    top_p=0.95,
    use_local_model=False,
):
    global stop_inference
    stop_inference = False  # Reset cancellation flag
    REQUEST_COUNTER.inc()  # Increment request counter
    request_timer = REQUEST_DURATION.time()  # Start timing the request

    try:
        # Initialize history if it's None
        if history is None:
            history = []

        if use_local_model:
            # Local inference
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
            raise NotImplementedError("API-based inference is not supported.")
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

        SUCCESSFUL_REQUESTS.inc()  # Increment successful request counter
    except Exception as e:
        FAILED_REQUESTS.inc()  # Increment failed request counter
        yield history + [(message, f"Error: {str(e)}")]
    finally:
        request_timer.observe_duration()  # Stop timing the request


def cancel_inference():
    global stop_inference
    stop_inference = True

# Custom CSS for a fancy look
custom_css = """
#main-container {
    background-color: #f0f0f0;
    font-family: 'Arial', sans-serif;
}

.gradio-container {
    max-width: 700px;
    margin: 0 auto;
    padding: 20px;
    background: white;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border-radius: 10px;
}

.gr-button {
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.gr-button:hover {
    background-color: #45a049;
}

.gr-slider input {
    color: #4CAF50;
}

.gr-chat {
    font-size: 16px;
}

#title {
    text-align: center;
    font-size: 2em;
    margin-bottom: 20px;
    color: #333;
}
"""

# Define the interface
with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("<h1 style='text-align: center;'>🌟 Fancy AI Chatbot 🌟</h1>")
    gr.Markdown("Interact with the AI chatbot using customizable settings below.")

    with gr.Row():
        system_message = gr.Textbox(value="You are a friendly Chatbot.", label="System message", interactive=True)
        use_local_model = gr.Checkbox(label="Use Local Model", value=False)

    with gr.Row():
        max_tokens = gr.Slider(minimum=1, maximum=2048, value=512, step=1, label="Max new tokens")
        temperature = gr.Slider(minimum=0.1, maximum=4.0, value=0.7, step=0.1, label="Temperature")
        top_p = gr.Slider(minimum=0.1, maximum=1.0, value=0.95, step=0.05, label="Top-p (nucleus sampling)")

    chat_history = gr.Chatbot(label="Chat")

    user_input = gr.Textbox(show_label=False, placeholder="Type your message here...")

    cancel_button = gr.Button("Cancel Inference", variant="danger")

    user_input.submit(respond, [user_input, chat_history, system_message, max_tokens, temperature, top_p, use_local_model], chat_history)

    cancel_button.click(cancel_inference)

if __name__ == "__main__":
    start_http_server(8000)  # Expose metrics on port 8000
    
    demo.launch(server_port=7860, share=False) 
