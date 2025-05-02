import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
import random
import time


# Google Gemini API setup
genai.configure(api_key="AIzaSyCMjUSPrycsWJfDYg7BNKr6dSyk3Gtt0J8")
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

# Category and template mappings
category_keywords_map = {
    "islamic": ["hadees", "prophet", "islamic", "jumma", "deen"],
    "git": ["git", "github", "repo", "pull", "commit"],
    "coding": ["code", "coding", "developer", "programming"],
    "comparison": ["vs", "comparison", "compare", "difference"],
    "technology": ["tech", "technology", "ai", "ml", "software"]
}

template_map = {
    "islamic": ("https://raw.githubusercontent.com/usaidabid/Codeswave-post-generator/main/template1.png", (255, 255, 255)),
    "git": ("https://raw.githubusercontent.com/usaidabid/Codeswave-post-generator/main/template2.png", (255, 255, 255)),
    "coding": ("https://raw.githubusercontent.com/usaidabid/Codeswave-post-generator/main/template3.png", (255, 255, 255)),
    "comparison": ("https://raw.githubusercontent.com/usaidabid/Codeswave-post-generator/main/template4.png", (29, 22, 92)),
    "technology": ("https://raw.githubusercontent.com/usaidabid/Codeswave-post-generator/main/template5.png", (29, 22, 92))
}
# Default template values
default_template_path =  "https://raw.githubusercontent.com/usaidabid/Codeswave-post-generator/main/images/template1.png"
default_color = (255, 255, 255)

# Streamlit UI
st.title("CodesWave Post Generator")
user_prompt = st.text_area("Enter your post topic(Give a detailed and clear prompt ):")
if st.button("Generate Post"):
    with st.spinner('Generating Post...'):
        time.sleep(2) 
    # Step 1: Generate post text from prompt using Google Gemini API
    response_text = model.generate_content(user_prompt)
    post_text = response_text.text
    

    # Extract keywords from user prompt
    keyword_prompt = f"Extract 1 to 2 short keywords (topics/themes) from this prompt: '{user_prompt}'. Return them in comma-separated lowercase format only."
    response_keywords = model.generate_content(keyword_prompt)
    keywords = response_keywords.text.strip().lower()
    
    # Step 2: Template selection based on keywords
    input_keywords = [k.strip().lower() for k in keywords.split(',')]
    matched_category = None
    for category, keyword_list in category_keywords_map.items():
        if any(k in keyword_list for k in input_keywords):
            matched_category = category
            break

    if matched_category:
        selected_template_path, text_color = template_map[matched_category]
    else:
        selected_template_path, text_color = default_template_path, default_color

     

    # Step 3: Image generation with PIL
    background = Image.open(selected_template_path)
    font_path = "arial.ttf"
    font_size = 30
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(background)
    img_width, img_height = background.size
    left_margin = 70
    right_margin = 70
    top_margin = 250
    bottom_margin = 100
    line_spacing = 20
    max_text_width = img_width - left_margin - right_margin

    # Function to wrap text
    def wrap_text(text, font, max_width):
        lines = []
        words = text.split()
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)  # Get bounding box
            width = bbox[2] - bbox[0]  # Calculate width from bounding box
            
            if width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    # Adjust font size
    def adjust_font_size(post_text, font, max_text_width):
        font_size = 30
        lines = wrap_text(post_text, font, max_text_width)
        total_height = sum([draw.textbbox((0, 0), line, font=font)[3] for line in lines]) + (len(lines) - 1) * line_spacing
        while total_height + top_margin + bottom_margin > img_height:
            font_size -= 2
            font = ImageFont.truetype(font_path, font_size)
            lines = wrap_text(post_text, font, max_text_width)
            total_height = sum([draw.textbbox((0, 0), line, font=font)[3] for line in lines]) + (len(lines) - 1) * line_spacing
        while total_height + top_margin + bottom_margin < img_height - 100:
            font_size += 2
            font = ImageFont.truetype(font_path, font_size)
            lines = wrap_text(post_text, font, max_text_width)
            total_height = sum([draw.textbbox((0, 0), line, font=font)[3] for line in lines]) + (len(lines) - 1) * line_spacing
        return font, lines

    font, lines = adjust_font_size(post_text, font, max_text_width)
    x = left_margin
    y = top_margin
    for line in lines:
        draw.text((x, y), line, font=font, fill=text_color)
        y += draw.textbbox((0, 0), line, font=font)[3] + line_spacing
    if y + bottom_margin > img_height:
        y = img_height - bottom_margin

    # Save the final image
    final_image_path = "final_post_image.png"
    background.save(final_image_path)

   

    # Add download button for the generated image
    with open(final_image_path, "rb") as f:
        st.download_button("Download post", f, file_name="final_post_image.png", mime="image/png")
