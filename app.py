%%writefile app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import re
import base64
import json

# Set Streamlit page configuration
st.set_page_config(
    page_title="Image Fetcher",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS Styles ---
st.markdown(
    """
    <style>
    /* Background gradient */
    body {
        background: linear-gradient(to bottom right, #1f4037, #99f2c8);
        color: white;
    }
    /* Center the main content */
    .main {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    /* Style the input box */
    .stTextInput > div > div > input {
        background-color: #1e1e1e;
        color: white;
        border: none;
        padding: 10px;
        border-radius: 5px;
    }
    /* Style the title */
    .title h1 {
        font-size: 3rem;
        color: #ffffff;
        text-shadow: 2px 2px #000000;
    }
    /* Style the button */
    .stButton > button {
        background-color: #ff7f50;
        color: white;
        border: none;
        padding: 0.75em 1.5em;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1rem;
    }
    .stButton > button:hover {
        background-color: #ff6333;
    }
    /* Style captions */
    .caption {
        text-align: center;
        font-size: 1.2rem;
        margin-top: 10px;
        text-shadow: 1px 1px #000000;
    }
    /* Remove footer */
    footer {visibility: hidden;}
    /* Remove hamburger menu */
    #MainMenu {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Functions ---
def fetch_first_image_url(query):
    """Fetches the URL of the first valid image from Bing Image Search."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko)"
        )
    }
    search_url = f"https://www.bing.com/images/search?q={query}"
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all 'a' tags with class 'iusc'
        a_tags = soup.find_all('a', class_='iusc')
        for a in a_tags:
            m = a.get('m')
            if m:
                # Parse the JSON in the 'm' attribute to extract the image URL
                m_json = json.loads(m)
                image_url = m_json.get('murl')
                if image_url:
                    return image_url  # Return the first valid image URL
    return None

def load_image_from_url(url):
    """Loads an image from a URL or base64 string."""
    try:
        if url.startswith('data:image'):
            # Handle base64 image data
            image_data = re.sub('^data:image/.+;base64,', '', url)
            image = Image.open(BytesIO(base64.b64decode(image_data)))

            # Check the image size, if too small, skip displaying
            if image.size[0] <= 1 or image.size[1] <= 1:
                return None
            return image
        else:
            response = requests.get(url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))

                # Check the image size, if too small, skip displaying
                if image.size[0] <= 1 or image.size[1] <= 1:
                    return None
                return image
    except Exception as e:
        st.error(f"Error loading image: {e}")
    return None

# --- Main Content ---
st.markdown("<div class='title'><h1>🎨 Welcome to Image Fetcher</h1></div>", unsafe_allow_html=True)

# Add a subtitle
st.markdown(
    "<h3 style='text-align: center; color: #f0f0f0;'>Find any type of image instantly!</h3>",
    unsafe_allow_html=True,
)

# Spacer
st.markdown("<br>", unsafe_allow_html=True)

# Create columns for layout
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Input for the character name
    character_name = st.text_input("", placeholder="Enter a character name...")
    search_button = st.button("Search 🔍")

    if search_button and character_name:
        query = f"{character_name}"
        st.markdown(f"<h4 style='text-align: center;'>Searching for: <em>{query}</em></h4>", unsafe_allow_html=True)
        with st.spinner('Fetching image...'):
            image_url = fetch_first_image_url(query)
            if image_url:
                image = load_image_from_url(image_url)
                if image:
                    # Display image
                    st.image(image, caption=f"Image of {character_name}", use_container_width=True)
                else:
                    st.markdown(
                        "<div class='caption'>The image is too small to display or could not be loaded.</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    "<div class='caption'>No image found. Please try again.</div>",
                    unsafe_allow_html=True,
                )