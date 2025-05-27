import streamlit as st
import base64
import io
import zipfile
from PIL import Image
from together import Together
from datetime import datetime, timedelta

T_Token = "a155f54cccdac0acdce9168344b51cea68a199592bdd341b06dd2e61bbc0209c"

st.set_page_config(
    page_title="FLUX AI"
)

st.markdown("""
<style>
    body {
        background: #ffffff;
        color: #000000;
    }
    .stTextInput > input {
        background-color: #ffffff;
        color: #000000;
        border-radius: 0;
    }
    .stButton > button {
        background: rgba(255,255,255,0.05);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        width: 100%;
        transition: background-color 0.3s, transform 0.2s;
    }
    .stButton > button:hover {
        background-color: rgba(255,255,255,0.1);
        color: #ffffff;
    }
    .stButton > button:focus {
        outline: none;
        background-color: rgba(255,255,255,0.1);
        color: #ffffff;
    }
    .stButton > button:active {
        outline: none;
        background-color: #0056b3;
        color: #ffffff;
    }
    .css-1dp5vir {
        background-color: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(15px);
    }
    .css-18e3th9 {
        padding-top: 2rem;
    }
    .stAlert > div {
        background-color: rgba(255, 0, 0, 0.3);
        color: #ffffff;
    }
    .loading-skeleton {
        background: linear-gradient(90deg, rgba(255, 255, 255, 0.3) 25%, rgba(255, 255, 255, 0.5) 50%, rgba(255, 255, 255, 0.3) 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: 12px;
        height: 300px;
        margin: 1rem 0;
    }
    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    .glassmorphism {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'last_generation_time' not in st.session_state:
    st.session_state.last_generation_time = None
if 'generation_count' not in st.session_state:
    st.session_state.generation_count = 0

EXAMPLE_PROMPTS = [
    "Select an example prompt...",
    "A serene Japanese garden with cherry blossoms at sunset",
    "Futuristic cyberpunk city with neon lights and flying cars at night",
    "Mystical forest with glowing mushrooms and fairy lights",
    "Abstract cosmic scene with swirling galaxies and nebulas"
]

def generate_images(prompt, num_images, aspect_ratio):
    client = Together(api_key=T_Token)
    images = []
    
    if aspect_ratio == "1:1":
        width, height = 1440, 1440
    elif aspect_ratio == "16:9":
        width, height = 1440, 810
    elif aspect_ratio == "9:16":
        width, height = 720, 1440
    elif aspect_ratio == "4:3":
        width, height = 1440, 1080
    else:
        width, height = 1440, 1440

    width = (width // 16) * 16
    height = (height // 16) * 16

    for _ in range(num_images):
        try:
            response = client.images.generate(
                prompt=prompt,
                model="black-forest-labs/FLUX.1-schnell-Free",
                width=width,
                height=height,
                steps=1,
                n=1,
                response_format="b64_json"
            )
            images.append(response.data[0].b64_json)
        except Exception as e:
            st.error(f"Error generating image: {str(e)}")
    
    return images

def save_image(b64_string):
    try:
        image_data = base64.b64decode(b64_string)
        image = Image.open(io.BytesIO(image_data))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_image_{timestamp}.png"
        
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        buffered.seek(0)
        return buffered, filename
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None, None

def create_zip_file():
    memory_zip = io.BytesIO()
    
    with zipfile.ZipFile(memory_zip, 'w') as zf:
        for image_data, filename in st.session_state.generated_images:
            zf.writestr(filename, image_data.getvalue())
    
    return memory_zip.getvalue()

st.title("FLUX AI",help="RATE LIMIT 6 IMGS/S")
st.markdown("### Generate unique images using advanced FLUX AI")

selected_prompt = st.selectbox("Try an example prompt", EXAMPLE_PROMPTS)

default_prompt = selected_prompt if selected_prompt != "Select an example prompt..." else ""
prompt = st.text_input(
    "Enter your prompt",
    value=default_prompt,
    placeholder="Describe the image you want to generate...",
    key="prompt_input"
)

col1, col2 = st.columns(2)
with col1:
    num_images = st.number_input("Number of images", min_value=1, max_value=4, value=1, step=1)
with col2:
    aspect_ratio = st.selectbox(
        "Aspect ratio",
        ["1:1", "16:9", "9:16", "4:3"],
        help="Choose the aspect ratio for your generated image"
    )

if st.button("Generate Images", use_container_width=True) or (prompt and st.session_state.generation_count < 6 and st.session_state.last_generation_time is None):
    current_time = datetime.now()
    if st.session_state.last_generation_time:
        time_diff = current_time - st.session_state.last_generation_time
        if time_diff < timedelta(seconds=1) and st.session_state.generation_count >= 6:
            st.error("Rate limit exceeded. Please wait a moment.")
            st.stop()
    
    loading_placeholder = st.empty()
    
    # Set loading skeleton size based on aspect ratio
    if aspect_ratio == "1:1":
        skeleton_height = "300px"
        skeleton_width = "300px"
    elif aspect_ratio == "16:9":
        skeleton_height = "169px"  # Adjusted height for 16:9
        skeleton_width = "300px"
    elif aspect_ratio == "9:16":
        skeleton_height = "300px"
        skeleton_width = "169px"  # Adjusted width for 9:16
    elif aspect_ratio == "4:3":
        skeleton_height = "225px"  # Adjusted height for 4:3
        skeleton_width = "300px"
    else:
        skeleton_height = "300px"
        skeleton_width = "300px"

    loading_placeholder.markdown(f"""
        <div class="loading-skeleton" style="height: {skeleton_height}; width: {skeleton_width};"></div>
    """, unsafe_allow_html=True)
    
    images = generate_images(prompt, num_images, aspect_ratio)
    
    st.session_state.last_generation_time = current_time
    st.session_state.generation_count = (st.session_state.generation_count + num_images) % 6
    
    for b64_image in images:
        image_data, filename = save_image(b64_image)
        if image_data:
            st.session_state.generated_images.append((image_data, filename))
    
    loading_placeholder.empty()

if st.session_state.generated_images:
    st.markdown("### Image Gallery")

    cols = st.columns(3)
    st.session_state.generated_images = st.session_state.generated_images[::-1]

    for idx, item in enumerate(st.session_state.generated_images):
        if isinstance(item, tuple) and len(item) == 2:
            image_data, filename = item
            with cols[idx % 3]:
                st.markdown(f'<a href="data:image/png;base64,{base64.b64encode(image_data.getvalue()).decode()}" download="{filename}"><img src="data:image/png;base64,{base64.b64encode(image_data.getvalue()).decode()}" style="width:100%; border-radius: 15px; margin-bottom: 1rem;"></a>', unsafe_allow_html=True)
    st.download_button(
                label="Download ZIP",
                data=create_zip_file(),
                file_name="FLUX_AI.zip",
                mime="application/zip",
                key=f"download_button_{idx}",
                help="Click to download all generated images as a ZIP file",
    )

    # Add spacing before the button
    st.markdown("<br><br>", unsafe_allow_html=True)  # This adds vertical space

    # Add the Twitter/X card
    st.markdown("""
    <div style="background:rgba(255,255,255,0.05);text-align: center; margin-top: 20px; padding: 10px; border: 1px solid rgba(255,255,255,0.05); border-radius: 10px;">
        <a href="https://x.com/aditya_avadhoot" target="_blank" style="text-decoration: none; color: #000;">
            <span style="font-size: 20px; color:#ffffff;">Made with ❤️ Aditya</span>
        </a>
    </div>
    """, unsafe_allow_html=True)