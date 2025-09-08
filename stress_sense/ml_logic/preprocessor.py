import re

def strip_urls(text: str) -> str:
    """
    Remove URLs (http, https, www, youtu links) from a string.
    """
    # remove http/https URLs
    text = re.sub(r"http\S+", "", text)
    # remove www.* URLs
    text = re.sub(r"www\.\S+", "", text)
    # remove youtube short links
    text = re.sub(r"youtu\.be\S+", "", text)
    return text.strip()

def decode_label(label: int) -> str:
    """
    Decode a numeric label to its string representation.
    """
    if label == 0:
        return "Anxiety"
    elif label == 1:
        return "Normal"
    else:
        return "Stress"
