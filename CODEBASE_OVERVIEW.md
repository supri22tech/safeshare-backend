# SafeShare Codebase Overview

SafeShare is a privacy-centric social networking platform built with Django.

## Key Features
- **Automated Privacy Blurring**: Uses face recognition to detect users in photos and blurs them until consent is given.
- **Identity Verification**: OCR-based Aadhaar processing to verify age and prevent identity theft.
- **Blockchain Integration**: Immutable recording of post metadata on an Ethereum blockchain.
- **Parental Controls**: Allows parents to monitor the social activity of minor users.

## Technical Stack
- **Backend**: Django (Python)
- **Database**: MySQL
- **AI/ML**: OpenCV, Face Recognition (dlib), Tesseract OCR
- **Blockchain**: Web3.py, Solidity, Ganache
