import streamlit as st
import requests
import io
from PIL import Image
import time  # Add this at the top with other imports
import base64
import threading

# Page config   
st.set_page_config(
    page_title="FLUX AI"
)

# Custom CSS for dark theme and modern UI
st.markdown("""
<style>
    .stTextInput > div > div > input {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    .stButton > button {
        background-color: #4b4b4b;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #606060;
    }
    .css-1dp5vir {
        background-color: #1a1a1a;
    }
    .css-18e3th9 {
        padding-top: 2rem;
    }
    .stAlert > div {
        background-color: #2b2b2b;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.title("FLUX AI")
st.markdown("Generate unique images using advanced AI")

# API configuration
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": "Bearer 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"}  # Replace with your API key

def generate_image(prompt, index=0, aspect_ratio="1:1"):
    try:
        # Add some variation to the prompt for multiple images
        if index > 0:
            variations = [
                " with different lighting and perspective",
                " in a different style",
                " with alternative composition",
                " from another angle"
            ]
            prompt = prompt + variations[index - 1]

        # Set width and height based on aspect ratio
        aspect_ratios = {
            "1:1": (512, 512),
            "16:9": (768, 432),
            "9:16": (432, 768),
            "3:4": (384, 512),
            "4:3": (512, 384)
        }
        width, height = aspect_ratios[aspect_ratio]

        response = requests.post(
            API_URL, 
            headers=headers, 
            json={
                "inputs": prompt,
                "parameters": {
                    "width": width,
                    "height": height
                }
            }
        )
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            st.error(f"Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Main app interface
with st.container():
    # Example prompts section
    st.markdown("### Example prompts:")
    example_prompts = [
        "Select an example prompt...",
        "A serene Japanese garden with cherry blossoms at sunset, watercolor style",
        "Futuristic cyberpunk city with neon lights and flying cars at night",
        "Mystical forest with glowing mushrooms and fairy lights",
        "Abstract cosmic scene with swirling galaxies and nebulas"
    ]
    
    selected_prompt = st.selectbox("Try an example prompt", example_prompts)

    # Prompt input section
    default_prompt = selected_prompt if selected_prompt != "Select an example prompt..." else ""
    prompt = st.text_input(
        "Enter your prompt",
        value=default_prompt,
        placeholder="Describe the image you want to generate...",
        key="prompt_input"
    )

    # Image settings section
    col1, col2 = st.columns(2)
    with col1:
        num_images = st.number_input("Number of images", min_value=1, max_value=4, value=1, step=1)
    with col2:
        aspect_ratio = st.selectbox(
            "Aspect ratio",
            ["1:1", "16:9", "9:16", "3:4", "4:3"],
            help="Choose the aspect ratio for your generated image"
        )

    # Generate button
    col1, col2 = st.columns([3, 1])
    with col1:
        generate_button = st.button("Generate Image", use_container_width=True)

    if generate_button and prompt:
        start_time = time.time()
        
        # Create timer placeholder
        timer_placeholder = st.empty()
        
        # Function to update timer
        def update_timer():
            while True:  # Loop to keep updating the timer
                current_time = time.time()
                elapsed_time = current_time - start_time
                timer_placeholder.info(f"Generation time: {elapsed_time:.2f} seconds")
                time.sleep(0.5)  # Update every 0.5 seconds

        # Start the timer update in a separate thread
        timer_thread = threading.Thread(target=update_timer)
        timer_thread.start()

        # Create placeholder containers for skeletons
        st.markdown("### Generated Images")
        
        # CSS for Pinterest-like grid
        st.markdown("""
            <style>
                .generated-images {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 16px;
                    padding: 16px;
                }
                .image-card {
                    position: relative;
                    background: #2b2b2b;
                    border-radius: 10px;
                    overflow: hidden;
                    transition: transform 0.2s;
                }
                .image-card:hover {
                    transform: translateY(-5px);
                }
                .skeleton {
                    background: linear-gradient(90deg, #2b2b2b 25%, #3b3b3b 50%, #2b2b2b 75%);
                    background-size: 200% 100%;
                    animation: shimmer 1.5s infinite;
                    border-radius: 10px;
                }
                @keyframes shimmer {
                    0% { background-position: -200% 0; }
                    100% { background-position: 200% 0; }
                }
            </style>
        """, unsafe_allow_html=True)

        # Create placeholders for all images first
        image_placeholders = []
        for i in range(num_images):
            placeholder = st.empty()
            with placeholder:
                # Adjust skeleton height based on aspect ratio
                aspect_ratios_height = {
                    "1:1": "300px",
                    "16:9": "169px",
                    "9:16": "533px",
                    "3:4": "400px",
                    "4:3": "300px"
                }
                skeleton_height = aspect_ratios_height[aspect_ratio]
                
                st.markdown(f"""
                    <div class="image-card">
                        <div class="skeleton" style="height: {skeleton_height};"></div>
                    </div>
                """, unsafe_allow_html=True)
            image_placeholders.append(placeholder)

        # Generate images
        for i in range(num_images):
            # Update timer
            update_timer()
            
            # Generate image
            image = generate_image(prompt, i, aspect_ratio)
            if image:
                # Save image to BytesIO for downloading
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Replace skeleton with generated image
                with image_placeholders[i]:
                    st.markdown(f"""
                        <div class="image-card">
                            <img src="data:image/png;base64,{base64.b64encode(img_byte_arr).decode()}" 
                                 style="width: 100%; height: auto; border-radius: 10px;" />
                            <div style="position: absolute; bottom: 0; left: 0; right: 0; text-align: center;">
                                <button class="download-button" onclick="window.open('data:image/png;base64,{base64.b64encode(img_byte_arr).decode()}', '_blank')">Download</button>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        # Final timer update
        end_time = time.time()
        generation_time = end_time - start_time
        timer_placeholder.success(f"Generation completed in {generation_time:.2f} seconds")

    # Display usage instructions
    with st.expander("Usage Instructions"):
        st.markdown("""
        1. Enter a descriptive prompt in the text field
        2. Click the 'Generate Image' button
        3. Wait for the AI to generate your image
        4. The generated image will appear below
        
        Note: More detailed prompts often lead to better results.
        """)

    # Error handling
    if generate_button and not prompt:
        st.warning("Please enter a prompt before generating.")