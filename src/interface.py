"""
src/interface.py
"""


import gradio as gr
import pandas as pd
import os
import base64
from datetime import datetime
from pdf2image import convert_from_path
from dotenv import load_dotenv
from src.run_generators import generate_pdf_from_excel
from src.sender import send_pdf_via_email
from src.slack import post_to_slack
from src.webhook import post_webhook_message


load_dotenv()

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)


def process_excel(file, email, slack, webhook, use_dummy):

    if use_dummy:
        file_path = "data/sample_products.xlsx"
    elif file is not None:
        file_path = file.name
    else:
        return None, "Please upload a file or use the example one.", None, None
    
    df = pd.read_excel(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(TEMP_DIR, f"product_sheet_{timestamp}.pdf")

    # Save temp Excel and generate PDF
    df.to_excel("temp/_preview.xlsx", index=False)
    generate_pdf_from_excel("temp/_preview.xlsx", output_path)
    print(f"Generated: {output_path}")

    # Convert image to thumnail
    images = convert_from_path(output_path, first_page=1, last_page=2)
    image_paths = []

    for idx, img in enumerate(images):
        img_path = os.path.join(TEMP_DIR, f"{timestamp}_preview_{idx+1}.jpg")
        img.save(img_path, "JPEG")
        image_paths.append(img_path)
    else:
        image_path = None

    if email:
        send_pdf_via_email(output_path)
    if slack:
        post_to_slack(output_path)
    if webhook:
        post_webhook_message(os.getenv("WEBHOOK_URL"), output_path)

    return df, "PDF generated successfully!", output_path, image_paths

with gr.Blocks(title="PDF Generator Interface") as demo:
    gr.Markdown("PDF Product Sheet Generator - Nested{Loop}")

    with gr.Row():
        with gr.Column():
            use_dummy = gr.Checkbox(label="Use example file", value=False)
            file_input = gr.File(label="Upload Excel File", file_types=[".xlsx"])
            email_box = gr.Checkbox(label="Send Email")
            slack_box = gr.Checkbox(label="Post to Slack")
            webhook_box = gr.Checkbox(label="Trigger Webhook")

    preview = gr.Dataframe(label="Excel Preview")
    status = gr.Textbox(label="Status")
    download = gr.File(label="Download PDF")
    image_preview = gr.Gallery(label="PDF Preview Pages")
    generate_btn = gr.Button("Generate PDF")

    generate_btn.click(
        fn=process_excel,
        inputs=[file_input, email_box, slack_box, webhook_box, use_dummy],
        outputs=[preview, status, download, image_preview]
    )

demo.launch(share=False, inbrowser=True)