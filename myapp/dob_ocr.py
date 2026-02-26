# Pytesseract OCR
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import re
import numpy as np
import cv2
import os

tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    pytesseract.pytesseract.tesseract_cmd = 'tesseract'

OCR_AVAILABLE = True


PSM_MODES = [
    '--psm 3',  # Fully automatic page segmentation (Default)
    '--psm 4',  # Assume a single column of text
    '--psm 6',  # Assume a single uniform block of text
    '--psm 11', # Sparse text - find as much text as possible
    '--psm 12', # Sparse text with OSD
    '--psm 13', # Raw line mode
]


def apply_sharpen(img):
    kernel = np.array([[-1,-1,-1],
                       [-1, 9,-1],
                       [-1,-1,-1]])
    sharpened = cv2.filter2D(img, -1, kernel)
    return sharpened


def apply_unsharp_mask(img):
    blurred = cv2.GaussianBlur(img, (0, 0), 3.0)
    unsharp = cv2.addWeighted(img, 1.5, blurred, -0.5, 0)
    return unsharp


def remove_glare(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 200], dtype=np.uint8)
    upper_white = np.array([180, 30, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower_white, upper_white)
    mask = cv2.bitwise_not(mask)
    result = cv2.bitwise_and(img, img, mask=mask)
    return result


def adjust_gamma(img, gamma=1.5):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255
                     for i in range(256)]).astype("uint8")
    return cv2.LUT(img, table)


def preprocess_image_variants(image_path):
    img = cv2.imread(image_path)
    if img is None:
        pil_img = Image.open(image_path).convert('RGB')
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    variants = []
    
    # Original
    variants.append(('original', Image.fromarray(gray)))
    
    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    variants.append(('clahe', Image.fromarray(enhanced)))
    
    # Binary threshold
    _, thresh_binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    variants.append(('binary', Image.fromarray(thresh_binary)))
    
    # Otsu's threshold
    _, thresh_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(('otsu', Image.fromarray(thresh_otsu)))
    
    # Denoised
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    variants.append(('denoised', Image.fromarray(denoised)))
    
    # Sharpened
    sharpened = apply_sharpen(gray)
    variants.append(('sharpened', Image.fromarray(sharpened)))
    
    # Unsharp mask
    unsharp = apply_unsharp_mask(gray)
    variants.append(('unsharp', Image.fromarray(unsharp)))
    
    # Gamma correction (brighten)
    gamma_corrected = adjust_gamma(gray, 1.5)
    variants.append(('gamma', Image.fromarray(gamma_corrected)))
    
    # Denoised + CLAHE
    denoised_clahe = clahe.apply(denoised)
    variants.append(('denoised_clahe', Image.fromarray(denoised_clahe)))
    
    # Denoised + Sharpen
    denoised_sharpen = apply_sharpen(denoised)
    variants.append(('denoised_sharpen', Image.fromarray(denoised_sharpen)))
    
    # CLAHE + Sharpen
    clahe_sharpen = apply_sharpen(enhanced)
    variants.append(('clahe_sharpen', Image.fromarray(clahe_sharpen)))
    
    # High contrast
    contrast_enhanced = cv2.equalizeHist(gray)
    variants.append(('histogram', Image.fromarray(contrast_enhanced)))
    
    # Morphological gradient
    kernel = np.ones((3,3), np.uint8)
    morph = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
    variants.append(('morphology', Image.fromarray(morph)))
    
    return variants


def preprocess_variants(image_path):
    if not OCR_AVAILABLE:
        return [('original', Image.open(image_path))]
    
    original = Image.open(image_path).convert('L')
    variants = [('original', original)]
    variants.extend(preprocess_image_variants(image_path))
    return variants


def extract_text_with_config(img, config):
    try:
        if hasattr(img, 'convert'):
            img = img.convert('RGB')
        result = pytesseract.image_to_string(img, config=config)
        if result:
            return result
        return ""
    except Exception as e:
        print(f"OCR Error: {e}")
        import traceback
        traceback.print_exc()
        return ""


def sanitize_name(name):
    if not name:
        return None
    # Remove special characters, keep only letters and spaces
    cleaned = re.sub(r'[^a-zA-Z\s]', '', name)
    # Remove extra spaces
    cleaned = ' '.join(cleaned.split())
    # Title case
    cleaned = cleaned.title()
    return cleaned.strip() if cleaned.strip() else None


def sanitize_aadhaar(aadhaar):
    if not aadhaar:
        return None
    # Keep only digits
    cleaned = re.sub(r'\D', '', aadhaar)
    # Should be 12 digits
    if len(cleaned) == 12:
        return cleaned
    return None


def sanitize_dob(dob):
    if not dob:
        return None
    # Match DD/MM/YYYY or DD-MM-YYYY
    match = re.search(r'(\d{2})[/-](\d{2})[/-](\d{4})', dob)
    if match:
        day, month, year = match.groups()
        # Validate day and month ranges
        if 1 <= int(day) <= 31 and 1 <= int(month) <= 12:
            return f"{day}/{month}/{year}"
    return None


def sanitize_gender(gender):
    if not gender:
        return None
    gender_lower = gender.lower()
    if 'male' in gender_lower:
        return 'Male'
    elif 'female' in gender_lower:
        return 'Female'
    return gender.title()


def extract_details(image_path):
    if not OCR_AVAILABLE:
        print("OCR not available - Pytesseract not installed")
        return None, None, None, None, ""
    
    print(f"Processing image: {image_path}")
    
    variants = preprocess_variants(image_path)
    print(f"Number of variants: {len(variants)}")
    
    all_results = []
    
    for label, img in variants:
        for psm in PSM_MODES:
            config = psm
            text = extract_text_with_config(img, config)
            
            if not text.strip():
                continue
            
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            
            # Debug: print lines for first few variants
            if label == 'original' and psm == '--psm 3':
                print(f"Lines: {lines[:15]}")
            
            dob = None
            name = None
            aadhaar = None
            gender = None
            
            for line in lines:
                line_lower = line.lower()
                dob_match = re.search(r"(\d{2}[/-]\d{2}[/-]\d{4})", line)
                if dob_match:
                    if 'dob' in line_lower or 'date of birth' in line_lower:
                        dob = dob_match.group(1)
                    elif not dob:
                        dob = dob_match.group(1)
                
                aadhaar_match = re.search(r"(\d{4}\s?\d{4}\s?\d{4})", line)
                if aadhaar_match and not aadhaar:
                    aadhaar = aadhaar_match.group(1).replace(' ', '')
                
                aadhaar_match2 = re.search(r"(\d{12})", line)
                if aadhaar_match2 and not aadhaar:
                    aadhaar = aadhaar_match2.group(1)
                
                gender_match = re.search(r"\b(Male|Female|MALE|FEMALE)\b", line, re.IGNORECASE)
                if gender_match:
                    gender = gender_match.group(1).title()
            
            name_candidates = []
            
            for i, line in enumerate(lines):
                if re.search(r"\d{2}[/-]\d{2}[/-]\d{4}", line):
                    if i > 0:
                        name_candidates.append(lines[i - 1])
                    if i > 1:
                        name_candidates.append(lines[i - 2])
            
            name_label_match = re.search(r"Name[:\s]+([A-Za-z\s]+?)(?:\n|$)", text, re.IGNORECASE)
            if name_label_match:
                name_candidates.append(name_label_match.group(1))
            
            dob_pos = text.lower().find('dob')
            if dob_pos > 0:
                before_dob = text[:dob_pos].strip()
                words_before_dob = before_dob.split()
                if len(words_before_dob) >= 2:
                    potential_name = ' '.join(words_before_dob[-5:]) if len(words_before_dob) > 5 else before_dob
                    name_candidates.append(potential_name)
            
            name_patterns = [
                r"(?:Mr\.|Ms\.|Mrs\.|Miss|Master)\s+([A-Za-z]+(?:\s+[A-Za-z]+){1,3})",
                r"(?:S\/O|D\/O|W\/O|Father|Mother)[:\s]+([A-Za-z]+(?:\s+[A-Za-z]+){1,3})",
                r"([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z]\.?\.?)?(?:\s+[A-Z]\.?\.?)?)",
                r"([A-Za-z]+\s+[A-Za-z]+\s+[A-Z]\s+[A-Z])$",
            ]
            for pattern in name_patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    name_candidates.append(match.group(1))
            
            common_non_names = [
                "government", "india", "female", "male", "year", "dob", "birth",
                "father", "mother", "address", "village", "road", "pin", "aadhaar",
                "proof", "identity", "citizenship", "date", "birth", "used",
                "verification", "online", "authentication", "scanning", "qr",
                "code", "offline", "xml", "should", "with", "not", "of", "is",
                "the", "and", "this", "that", "for", "are", "but", "hrt",
                "het", "urr", "31ur", "4ftut", "tfodl", "ufafafu", "jquil",
                "yapfcvur", "vatqvd", "fabfm", "4y3r", "1st", "31fa", "4ait", "aifey",
                "gites", "proof", "emme", "shri", "sri", "enroll", "enrollment",
                "aadhaar", "sipersst", "trae", "fear", "art", "arfee"
            ]
            
            extracted_name = None
            best_name_len = 0
            
            for candidate in name_candidates:
                lower_candidate = candidate.lower()
                if any(x in lower_candidate for x in common_non_names):
                    continue
                
                cleaned = re.sub(r'[^A-Za-z\s]', '', candidate).strip()
                words = cleaned.split()
                valid_words = [w for w in words if len(w) >= 2]
                
                if valid_words:
                    name_str = ' '.join(valid_words)
                    name_len = len(name_str.replace(' ', ''))
                    if name_len >= 4 and name_len > best_name_len:
                        has_only_initials = all(len(w) <= 2 for w in words)
                        if not has_only_initials or len(words) >= 3:
                            extracted_name = name_str
                            best_name_len = name_len
            
            name = None
            
            # Primary strategy: Look for name in lines that appear just before DOB line
            for i, line in enumerate(lines):
                line_lower = line.lower()
                if 'dob' in line_lower or 'date of birth' in line_lower:
                    # Check previous lines for name
                    for j in range(max(0, i-3), i):
                        candidate = lines[j].strip()
                        candidate_lower = candidate.lower()
                        
                        # Skip invalid candidates
                        if any(x in candidate_lower for x in ['government', 'india', 'male', 'female', 'proof', 'identity', 'aadhaar', 'issued', 'date']):
                            continue
                        if candidate.isdigit():
                            continue
                        if len(candidate) < 5:
                            continue
                        
                        name = candidate
                        print(f"Found name before DOB: {name}")
                        break
                    if name:
                        break
            
            # Secondary strategy: Look for 2-3 word names with initials
            if not name:
                for line in lines:
                    line_clean = line.strip()
                    lower_line = line_clean.lower()
                    
                    if any(x in lower_line for x in ['government', 'india', 'male', 'female', 'proof', 'identity', 'aadhaar', 'issued', 'date of birth', 'dob']):
                        continue
                    
                    words = line_clean.split()
                    
                    # Pattern: FirstName Initial or FirstName MiddleInitial Initial (e.g., "Yash M" or "John P S")
                    if len(words) >= 2 and len(words) <= 4:
                        # Check if has valid name pattern
                        valid = True
                        for w in words:
                            if w.isdigit():
                                valid = False
                                break
                            if len(w) == 1 and not w.isalpha():
                                valid = False
                                break
                        
                        if valid:
                            # Must have at least one word with 3+ chars
                            if any(len(w) >= 3 for w in words):
                                name = line_clean
                                print(f"Found name pattern: {name}")
                                break
            
            # Skip if name contains numbers
            if name and any(c.isdigit() for c in name):
                name = None
            
            score = len(text)
            
            # Only add result if we found a valid name
            if name:
                all_results.append({
                    'label': f"{label}_{psm.replace(' ', '_').replace('--', '')}",
                    'dob': dob,
                    'name': name,
                    'aadhaar': aadhaar,
                    'gender': gender,
                    'text': text,
                    'score': score
                })
    
    best_dob = None
    best_name = None
    best_aadhaar = None
    best_gender = None
    best_text = ""
    
    # Count name occurrences to find the most common valid name
    name_counts = {}
    for result in all_results:
        if result['name']:
            # Normalize name (lowercase, remove extra spaces)
            normalized = ' '.join(result['name'].lower().split())
            name_counts[normalized] = name_counts.get(normalized, 0) + 1
    
    # Find the most common name
    if name_counts:
        best_name = max(name_counts.keys(), key=lambda x: (name_counts[x], -len(x)))
    
    for result in all_results:
        if result['dob'] and not best_dob:
            best_dob = result['dob']
        if result['aadhaar'] and (not best_aadhaar or len(result['aadhaar']) > len(best_aadhaar)):
            best_aadhaar = result['aadhaar']
        if result['gender'] and not best_gender:
            best_gender = result['gender']
        if result['score'] > len(best_text):
            best_text = result['text']
    
    # Sanitize outputs
    best_name = sanitize_name(best_name)
    best_aadhaar = sanitize_aadhaar(best_aadhaar)
    best_dob = sanitize_dob(best_dob)
    best_gender = sanitize_gender(best_gender)
    
    print(f"DOB: {best_dob}, Name: {best_name}, Aadhaar: {best_aadhaar}, Gender: {best_gender}")
    return best_dob, best_name, best_aadhaar, best_gender, best_text


if __name__ == "__main__":
    print("=========================")
    p = input("Enter image path: ")
    dob, name, aadhaar, gender, text = extract_details(p)
    
    with open(r"C:\Users\lenovo\PycharmProjects\safeshare\myapp\extracted_details.txt", "w", encoding="utf-8") as f:
        f.write(f"Name: {name if name else 'Not found'}\n")
        f.write(f"DOB: {dob if dob else 'Not found'}\n")
        f.write(f"Aadhaar: {aadhaar if aadhaar else 'Not found'}\n")
        f.write(f"Gender: {gender if gender else 'Not found'}\n")
        f.write(f"\n--- Full Text ---\n{text}\n")

    print("Saved to extracted_details.txt")
