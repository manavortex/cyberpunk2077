from PIL import Image, ImageColor, ImageDraw, ImageFont
import os

# Path to your default icon (update this to your actual file path)
input_image_path = "C:\\ReshadeScreenshotsTemp\\_icons\\high_school_stuff\\sweatshirt_default.png"

# Define your color map (appearance_name: rgb_color)
color_map = {
    "gambeson_green": "#4B6F44",     "black_green_2": "#1A2E1A",    "black_green_1": "#223322",    "gambeson": "#C4BAA8",    "silver_foil": "#D0D5DC",
    "dyed_red": "#A83232",    "brown_dirty": "#5C4A3A",    "shiny_green": "#3D8B3D",    "white_stripes": "#F0F0F0",    "olive_nylon": "#6B8E23",
    "red_gray_white": "#C0A9A9",    "dyed_gray": "#808080",    "voodoo_red": "#8B0000",    "black_gold": "#332C12",    "pink_green": "#C48E9D",
    "yellow_poor": "#D4A017",    "violet_pattern": "#6A5ACD",    "leather_orange": "#B87333",    "blue_dyed": "#3A5FCD",    "olive": "#556B2F",
    "black": "#000000",    "white": "#ffffff",    "grey": "#dfdfdf",    "dark_grey": "#bcbcbc",
}

color_map_polo = {
    "red": "#C00000",                # Classic bold red
    "white": "#fff",              # Slightly off-white for fabric texture
    "rich_02": "#3A3A3A",            # Dark sophisticated gray
    "rich_01": "#5D432C",            # Rich brown (like mahogany)
    "gold": "#D4AF37",               # Metallic gold
    "roses01": "#E66767",            # Soft rose red
    "roses02": "#DB4D4D",            # Deeper rose red
    "heart": "#FF6B6B",              # Valentine heart red
    "pink": "#FFB6C1",               # Classic light pink
    "blue_pattern": "#4169E1",       # Royal blue for patterns
    "pink_pattern": "#FF69B4",       # Hot pink for patterns
    "gold_pattern": "#FFD700",       # Brighter gold for patterns
    "black_white_rich": "#2C2C2C",   # Deep black with white elements
    "blue_red": "#1E3F8B",           # Navy blue with red accents
    "purple_camo": "#9370DB",        # Dusty purple for camo
    "purple_pattern": "#800080",     # Regal purple for patterns
    "yellow_old": "#CCAA44",         # Aged, muted yellow
    "test": "#FF0000",               # Bright red for testing
    "white_orig": "#F8F8F8",         # Pure white duplicate
    "black": "#000000"               # Pure black
}


def add_text_to_image(image, text):
    """Adds text label to the image"""
    try:
        draw = ImageDraw.Draw(image)

        # Use a basic font (you may need to specify a font file)
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()

        # Calculate text position (centered at bottom)
        text_width = draw.textlength(text, font=font)
        x = (image.width - text_width) / 2
        y = image.height - 20  # 20px from bottom

        # Add text with contrasting outline
        draw.text((x-1, y-1), text, font=font, fill="white")
        draw.text((x+1, y-1), text, font=font, fill="white")
        draw.text((x-1, y+1), text, font=font, fill="white")
        draw.text((x+1, y+1), text, font=font, fill="white")
        draw.text((x, y), text, font=font, fill="black")

    except Exception as e:
        print(f"Couldn't add text: {e}")
    return image

def colorize_white_icon(image_path, color_map):
    """Main processing function"""
    try:
        original_img = Image.open(image_path).convert("RGBA")
        dir_path = os.path.dirname(image_path)
        base_name = os.path.basename(image_path)

        if "_default" in base_name:
            base_name = base_name.replace("_default", "")
        base_name = os.path.splitext(base_name)[0]

        for appearance_name, color_value in color_map.items():
            if isinstance(color_value, str):
                rgb_color = ImageColor.getrgb(color_value)
            else:
                rgb_color = color_value

            colored_img = replace_white_with_color(original_img, rgb_color)

            # Add the appearance name as text
            colored_img = add_text_to_image(colored_img, appearance_name)

            output_path = os.path.join(dir_path, f"{base_name}_{appearance_name}.png")
            colored_img.save(output_path, "PNG")
            print(f"Saved: {output_path}")

    except Exception as e:
        print(f"Error: {e}")

def replace_white_with_color(original_img, rgb_color):
    """Same as before..."""
    colored_img = Image.new("RGBA", original_img.size)
    for x in range(original_img.width):
        for y in range(original_img.height):
            r, g, b, alpha = original_img.getpixel((x, y))
            if alpha > 0:
                colored_img.putpixel((x, y), (*rgb_color, alpha))
            else:
                colored_img.putpixel((x, y), (0, 0, 0, 0))
    return colored_img

if __name__ == "__main__":
    colorize_white_icon(input_image_path, color_map)
