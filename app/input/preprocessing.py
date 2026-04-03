import re
import unicodedata

def clean_text(text: str) -> str:
    # Lowercase
    text = text.lower()

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Unicode normalization
    text = unicodedata.normalize('NFKC', text)

    # Remove emojis (basic)
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    return text

# Handles:

#Lowercasing
#Whitespace cleanup
#Unicode normalization
#Emoji removal