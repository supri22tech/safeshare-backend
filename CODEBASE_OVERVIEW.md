# SafeShare Codebase Overview

SafeShare is a privacy-centric social networking platform built with Django. It integrates AI for privacy protection and Blockchain for data integrity.

## Key Features
- **Automated Privacy Blurring**: Uses face recognition to detect users in photos and blurs them until consent is given.
- **Identity Verification**: OCR-based Aadhaar processing to verify age and prevent identity theft.
- **Blockchain Integration**: Immutable recording of post metadata on an Ethereum blockchain.
- **Parental Controls**: Allows parents to monitor the social activity of minor users.

## Core Functions Breakdown

### 1. Identity & Verification
*   **`android_user_registration` (`views.py`)**: Orchestrates user creation, Aadhaar OCR verification, and age-based classification.
*   **`extract_details` (`dob_ocr.py`)**: Uses Tesseract to extract Name and DOB from Aadhaar cards.
*   **`theftdetection` (`views.py`)**: Uses face recognition to ensure a new user isn't impersonating an existing one.

### 2. Privacy & Content
*   **`post_insert` (`views.py`)**: Handles new posts, face detection, automated blurring of non-consenting users, and blockchain logging.
*   **`rec_face_image` (`recognize_face.py`)**: The primary AI engine for identifying registered users in images.
*   **`accept_notification` (`views.py`)**: Re-processes images to remove blurs once a user grants consent.

### 3. Integration & Monitoring
*   **`upload_code` (`blockchainupload.py`)**: Commits post metadata to the local Ganache Ethereum network.
*   **`parent_view_activity` (`views.py`)**: Aggregates a child's social interactions for parental review.

## Technical Stack
- **Backend**: Django (Python)
- **Database**: MySQL
- **AI/ML**: OpenCV, Face Recognition (dlib), Tesseract OCR
- **Blockchain**: Web3.py, Solidity, Ganache
