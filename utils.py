import requests
import google.generativeai as genai
from config import GOOGLE_API_KEY, GENERATION_CONFIG, LEXICA_BASE_URL, STABILITY_AI_API_KEY
import streamlit as st
from tenacity import retry, wait_exponential, stop_after_attempt, after_log
import logging

# Configure Google AI
genai.configure(api_key=GOOGLE_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def generate_design_idea(style, size, rooms, model_name="gemini-1.5-flash", **kwargs):
    """
    Generate custom home design plan using Google's Gemini AI
    """
    # Extract additional parameters from kwargs
    room_details = kwargs.get('room_details', {})
    num_bedrooms = kwargs.get('num_bedrooms', 3)
    num_bathrooms = kwargs.get('num_bathrooms', 2)
    num_doors = kwargs.get('num_doors', 2)
    num_windows = kwargs.get('num_windows', 8)
    ceiling_height = kwargs.get('ceiling_height', 'Standard (8ft)')
    floor_material = kwargs.get('floor_material', 'Hardwood')
    additional_requirements = kwargs.get('additional_requirements', '')
    timeline = kwargs.get('timeline', 'Not specified')
    priority = kwargs.get('priority', 'Not specified')
    
    # Context for the AI model
    context = f"""
    You are an expert home designer and architect. Create a comprehensive custom home design plan with the following specifications:
    
    Style: {style}
    Size: {size}
    Number of Rooms: {rooms}
    
    Room Configuration:
    - Bedrooms: {num_bedrooms}
    - Bathrooms: {num_bathrooms}
    - Exterior Doors: {num_doors}
    - Windows: {num_windows}
    - Ceiling Height: {ceiling_height}
    - Floor Material: {floor_material}
    
    Room Details:
    {format_room_details(room_details)}
    
    Additional Requirements:
    {additional_requirements}
    
    Project Timeline: {timeline}
    Design Priority: {priority}
    
    Please provide a detailed design plan that includes:
    1. Overall layout and floor plan description
    2. Room-by-room breakdown with dimensions and purposes
    3. Architectural features and design elements
    4. Color scheme recommendations
    5. Material suggestions
    6. Lighting and electrical considerations
    7. Furniture and decor recommendations
    8. Outdoor space planning (if applicable)
    9. Energy efficiency considerations
    10. Estimated timeline and budget considerations
    11. Door and window placement strategy
    12. Storage solutions and organization
    13. Accessibility features
    14. Smart home integration recommendations
    15. Maintenance considerations
    
    Format the response in clear, organized Markdown with headers and bullet points.
    Make it detailed, practical, and tailored to the specified style and requirements.
    Consider the project timeline and priority in your recommendations.
    """
    
    try:
        # Initialize the model
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=GENERATION_CONFIG
        )
        
        # Start chat session
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [context],
                }
            ]
        )
        
        # Send message and get response
        response = chat_session.send_message(context)
        
        # Process the response
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'parts') and len(response.parts) > 0:
            return response.parts[0].text
        else:
            return "Unable to generate design. Please try again."
            
    except Exception as e:
        logger.error(f"Error generating design: {e}")
        return generate_fallback_design(style, size, rooms, room_details, num_bedrooms, num_bathrooms, 
                                      num_doors, num_windows, ceiling_height, floor_material, 
                                      additional_requirements, timeline, priority)

def format_room_details(room_details):
    """
    Format room details for the AI prompt
    """
    formatted_details = []
    for room_name, details in room_details.items():
        room_info = f"\n{room_name.replace('_', ' ').title()}:\n"
        for key, value in details.items():
            if isinstance(value, list):
                room_info += f"- {key.replace('_', ' ').title()}: {', '.join(value)}\n"
            else:
                room_info += f"- {key.replace('_', ' ').title()}: {value}\n"
        formatted_details.append(room_info)
    return "\n".join(formatted_details)

def generate_fallback_design(style, size, rooms, room_details, num_bedrooms, num_bathrooms, 
                           num_doors, num_windows, ceiling_height, floor_material, 
                           additional_requirements, timeline, priority):
    """
    Generate a fallback design plan when the AI model fails
    """
    return f"""
# Mock Design Plan (due to API quota exhaustion or error)

## 📋 Your Custom Home Design Plan

### 1. Overall Layout and Floor Plan Description
This **{style}** home, approximately **{size}** with **{rooms}** rooms, features an open-concept layout designed for modern living and efficient space utilization. The main living areas flow seamlessly, promoting interaction and natural light.

### 2. Room-by-Room Breakdown

*   **Living Room:** {room_details.get('living_room', {}).get('size', '18ft x 15ft')} - Spacious and bright, ideal for entertaining.
*   **Kitchen:** {room_details.get('kitchen', {}).get('size', '12ft x 10ft')} - Modern kitchen with island and ample storage.
*   **Master Bedroom:** {room_details.get('master_bedroom', {}).get('size', '14ft x 16ft')} - Ensuite bathroom and walk-in closet.
*   **Additional Bedrooms:** {num_bedrooms - 1} bedrooms of varying sizes
*   **Bathrooms:** {num_bathrooms} bathrooms, including master ensuite

### 3. Architectural Features and Design Elements
Clean lines, large windows ({num_windows} total), and a minimalist aesthetic define the **{style}** style. Features include:
* {ceiling_height} ceilings throughout
* {floor_material} flooring
* {num_doors} exterior doors strategically placed
* Large windows for natural light
* Open floor plan concept

### 4. Color Scheme Recommendations
Neutral palette with shades of gray, white, and beige. Accent colors like deep blues or forest greens can be introduced through decor.

### 5. Material Suggestions
* {floor_material} for main living areas
* Natural stone accents
* High-quality cabinetry
* Durable countertops
* Energy-efficient windows

### 6. Lighting and Electrical Considerations
* Recessed LED lighting throughout
* Smart home integration
* Ample power outlets in all rooms
* Accent lighting for architectural features

### 7. Furniture and Decor Recommendations
* Minimalist furniture with clean lines
* Focus on functional pieces
* Large abstract art pieces
* Indoor plants for warmth

### 8. Outdoor Space Planning
* Spacious patio/deck
* Landscaped garden area
* Outdoor entertainment space
* Storage for outdoor equipment

### 9. Energy Efficiency Considerations
* High-performance insulation
* Energy-efficient windows
* Smart thermostat
* LED lighting throughout
* Solar panel ready

### 10. Project Timeline and Budget
* Timeline: {timeline}
* Priority Focus: {priority}
* Estimated completion: Based on {timeline} timeline
* Budget considerations aligned with {priority} priority

### 11. Additional Features
{additional_requirements}

This design plan provides a starting point; further customization and professional consultation are recommended.
"""

@st.cache_data(ttl=86400)  # Cache for 24 hours
@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3), after=after_log(logger, logging.WARNING))
def fetch_image_from_lexica(style):
    """
    Fetch relevant images from Lexica.art based on design style
    """
    try:
        # Prepare search query
        search_query = f"{style} home design architecture interior"
        
        # Construct API URL
        params = {
            "q": search_query,
            "limit": 10
        }
        
        # Make API request
        response = requests.get(LEXICA_BASE_URL, params=params, timeout=10)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        
        # Parse response
        data = response.json()
        
        # Return first image URL if available
        if data.get("images") and len(data["images"]) > 0:
            return data["images"][0]["src"]
        else:
            logger.warning(f"No images found for style: {style}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network or HTTP error fetching image from Lexica: {e}")
        return None # Return None on request errors instead of re-raising
    except Exception as e:
        logger.error(f"Unexpected error fetching image: {e}")
        return None

def validate_inputs(style, size, rooms):
    """
    Validate user inputs
    """
    errors = []
    
    if not style or len(style.strip()) < 2:
        errors.append("Please enter a valid design style (minimum 2 characters)")
    
    if not size or len(size.strip()) < 1:
        errors.append("Please enter the home size")
    
    if not rooms or len(rooms.strip()) < 1:
        errors.append("Please enter the number of rooms")
    
    try:
        room_count = int(rooms)
        if room_count < 1 or room_count > 50:
            errors.append("Number of rooms should be between 1 and 50")
    except ValueError:
        errors.append("Number of rooms must be a valid number")
    
    return errors 

@st.cache_data(ttl=86400) # Cache for 24 hours
def generate_stability_image(style, size, rooms):
    """
    Generate an image using Stability AI API based on a detailed text prompt.
    """
    if not STABILITY_AI_API_KEY:
        logger.error("Stability AI API key is not set.")
        return None

    # Construct a detailed prompt for Stability AI
    # This prompt is crucial for generating relevant images.
    prompt = f"""a detailed architectural floor plan and layout of a {style} style home, {size} with {rooms} rooms, 
    technical blueprint style, showing room layouts, dimensions, and furniture placement, 
    professional architectural drawing, clean lines, precise measurements, 
    includes living areas, bedrooms, bathrooms, kitchen layout, 
    high resolution, technical drawing style, architectural plan view, 
    professional CAD-like rendering, with room labels and measurements"""
    
    # Stability AI API endpoint and model (using stable-diffusion-v1-6 or similar)
    # It's important to use the correct API endpoint and parameters based on Stability AI documentation.
    # For text-to-image, a common endpoint might be /v1/generation/{engine_id}/text-to-image
    # I'll use a placeholder for engine_id and then use web_search to confirm the details.
    engine_id = "stable-diffusion-v1-6" # Example engine ID
    api_host = "https://api.stability.ai"
    api_url = f"{api_host}/v1/generation/{engine_id}/text-to-image"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {STABILITY_AI_API_KEY}"
    }

    payload = {
        "text_prompts": [
            {
                "text": prompt
            }
        ],
        "cfg_scale": 7,
        "clip_guidance_preset": "FAST_BLUE",
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30,
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        
        response_data = response.json()
        
        # Stability AI typically returns base64 encoded images. We need to decode and return as data URL or save.
        # For Streamlit st.image, a base64 data URL is usually acceptable.
        if response_data and response_data.get("artifacts"):
            for i, artifact in enumerate(response_data["artifacts"]):
                if artifact["finishReason"] == "SUCCESS" and artifact["base64"]:
                    # Return the first successful image as a data URL
                    base64_data = artifact["base64"]
                    return f"data:image/png;base64,{base64_data}"
            logger.warning("No successful image artifact found from Stability AI.")
            return None
        else:
            logger.warning("No image data received from Stability AI.")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Network or HTTP error generating image from Stability AI: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error generating image from Stability AI: {e}")
        return None 