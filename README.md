# PDF-Automation
 
Generate beautiful, ready-to-share PDF product sheets from Excel files directly in your browser.
No installs, no setup — just upload your file and download the PDF.

[Live Demo](https://huggingface.co/spaces/MillieJackson/PDF-Automation)

**Built by Millie Jackson @Nested{Loop}**

## Features
- Excel to PDF in one click
- Preview before download (see Excel table + first pages of PDF)
- Option to use a sample Excel file if you don’t have one ready
- Clean, responsive interface built with Gradio

## Tech Stack

- Python 3.10+
- Gradio – Web interface
- FPDF2 – PDF generation
- Pandas – Data parsing & validation

## How to Use
Go to the [Live App](https://huggingface.co/spaces/MillieJackson/PDF-Automation)

1. Upload your own .xlsx file or tick Use example file
2. Preview your Excel and PDF output
3. Download the generated PDF

## How It Works
**1. Upload Excel or Use Sample**

Choose your own .xlsx file or load a built-in example for testing.

**2. Data Parsing**

Read the Excel file with Pandas, check that required columns exist, and clean up the data.

**3. PDF Generation**

Use FPDF2 to create a cover page, apply styling, and format product listings.

**4. Preview & Download**

Show the Excel data table and first two PDF pages in the browser before saving the final PDF.

## Example Excel Format

The app expects columns like this:

<img width="626" height="298" alt="image" src="https://github.com/user-attachments/assets/698e8ab5-3f19-4855-ac86-c89f9d49c767" />


💡 You can download and modify the provided sample file to get started instantly.

## High Level Flow
```
User Input (Excel or sample)
       │
       ▼
Pandas → Validate & Clean Data
       │
       ▼
FPDF2 → Build PDF pages
       │
       ▼
Preview in Gradio → Download PDF
```
## Repository Structure
```
PDF-Automation/
│
├── app.py                  # Main Gradio app entry point
├── requirements.txt        # Dependencies
│
├── data/                   # Sample Excel files
│
├── src/
│   ├── excel_parser.py     # Excel loading & validation
│   ├── pdf_generator.py    # PDF creation with FPDF2
│   ├── run_generators.py   # Glue between parsing & PDF generation
│
├── templates/              # HTML & font assets
│
└── README.md               # Project documentation
```

## About

**Author:** Millie Jackson

**Freelance Lab:** Nested{Loop}

**Portfolio (Coming Soon):** milliejackson.dev

**Hugging Face:** huggingface.co/MillieJackson LinkedIn: LinkedIn

---

## License
This repository is for demonstration and portfolio purposes only. Contact Millie to discuss commercial use, adaptations, or collaboration.
