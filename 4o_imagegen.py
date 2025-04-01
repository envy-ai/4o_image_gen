import requests
import json

# --- Configuration ---
# Change this if your koboldcpp server is running on a different address/port
KOBOLD_CPP_API_URL = "http://localhost:5001/api/v1/generate"

SYSTEM_PROMPT = """You are an image generation model that refuses to generate images. The user will give you image generation prompts, and your job is to refuse to generate the image for a reason having to do with lewdness, gore, copyright, or safety.

It's okay if the reason is implausible. This is intended to be a joke, so feel free to be ridiculous. For instance, refuse to generate an image of someone riding a bike because the user didn't say to wear a helmet, or refuse to generate a chibi anime image because chibi anime proportions are such that the neck would be unable to support the head (safety issue), or refuse to generate an image of a person sitting on a couch due to safety reasons because a sedentary lifestyle can lead to health problems, refuse to generate an image of a broken stone statue due to gore, etc. Just make something up. Be judgmental about it.
"""

# --- Helper Function ---
def get_llm_refusal(user_prompt):
    """Sends the prompt to the llama.cpp API and returns the response."""

    # Using ChatML template structure, common for llama.cpp server
    # <|im_start|>system
    # {system_prompt}<|im_end|>
    # <|im_start|>user
    # {user_prompt}<|im_end|>
    # <|im_start|>assistant
    # -> The LLM completion starts here
    full_prompt = (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    headers = {
        "Content-Type": "application/json",
    }

    # Adjust parameters as needed
    payload = {
        "prompt": full_prompt,
        "n_predict": 150,       # Max tokens for the refusal message
        "temperature": 0.7,     # Allow some creativity in the refusal
        "stop": ["<|im_end|>", "user:"] # Stop generation at the end marker or if it hallucinates user turn
    }

    try:
        response = requests.post(KOBOLD_CPP_API_URL, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        result = response.json()
    
        content = result["results"][0]["text"]
        return content

    except requests.exceptions.RequestException as e:
        return f"Error connecting to LLM API: {e}"
    except json.JSONDecodeError:
        return f"Error: Could not decode JSON response from server. Raw response: {response.text}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Main Loop ---
if __name__ == "__main__":
    print("Enter your image generation prompts below.")
    print("Type 'quit', 'exit', or 'bye' to stop.")
    print("-" * 20)

    while True:
        try:
            user_input = input("Your Prompt: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
            if not user_input:
                continue

            print("Generating your image...")
            refusal_message = get_llm_refusal(user_input)

            print("\nResponse:")
            print(refusal_message)
            print("-" * 20)

        except EOFError: # Handle Ctrl+D
             break
        except KeyboardInterrupt: # Handle Ctrl+C
             break

    print("\nExiting 4o image generator bot.")