import pytesseract
from PIL import Image
import re
import sys

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_details(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    print(lines)

    dob = None
    name = None

    # ---- FIND DOB LINE ----
    for i, line in enumerate(lines):
        dob_match = re.search(r"\d{2}/\d{2}/\d{4}", line)
        if dob_match:
            dob = dob_match.group()
            # ---- NAME IS PREVIOUS LINE ----
            if i > 0:
                possible_name = lines[i - 1]
                if not any(x in possible_name.lower() for x in ["government", "india", "female", "male"]):
                    name = possible_name
            break
    if name:
        name = re.sub(r'[^A-Za-z\s]', '', name).strip()
    return dob, name

# res=extract_details(r'C:\Users\lenovo\PycharmProjects\safeshare\media\011aa.jpeg')
# print(res)

if __name__ == "__main__":
    print("=========================")
    p = input()
    dob, name = extract_details(p)
    # ---- SAVE TO TXT FILE ----
    with open(r"C:\Users\lenovo\PycharmProjects\safeshare\myapp\extracted_details.txt", "w", encoding="utf-8") as f:
        f.write(f"Name: {name if name else 'Not found'}\n")
        f.write(f"DOB: {dob if dob else 'Not found'}\n")

    print("Saved to extracted_details.txt")

    # C:\Users\lenovo\PycharmProjects\safeshare\media\