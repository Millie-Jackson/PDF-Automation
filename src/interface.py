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
from .utils import demo_df as _demo_df, save_mapping, load_mapping, apply_transforms


load_dotenv()

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)


def demo_df() -> pd.DataFrame:
    """Public helper for tests/UI; wraps utils.demo_df()."""
    return _demo_df()

def process_excel(file, email, slack, webhook, use_dummy):

    if use_dummy:
        input_path = "data/sample_products.xlsx"
    elif file is not None:
        # Gradio provides either .name or .tempfile; .name is widely supported
        input_path = getattr(file, "name", None) or getattr(file, "path", None)
        if not input_path or not os.path.exists(input_path):
            return None, "Uploaded file path not found.", None, []
    else:
        return None, "Please upload a file or tick 'Use example file'.", None, []
    
    try:
        df = pd.read_excel(input_path)
    except Exception as e:
        return None, f"Failed to read Excel: {e}", None, []

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_pdf = os.path.join(TEMP_DIR, f"product_sheet_{timestamp}.pdf")
    try:
        generate_pdf_from_excel(input_path, output_pdf)
    except Exception as e:
        return df, f"PDF generation error: {e}", None, []
    
    gallery_paths = []
    try:
        pages = convert_from_path(output_pdf, first_page=1, last_page=2)
        for idx, img in enumerate(pages, start=1):
            img_path = os.path.join(TEMP_DIR, f"{timestamp}_preview_{idx}.jpg")
            img.save(img_path, "JPEG")
            gallery_paths.append(img_path)
    except Exception as e:
        # Don't fail the whole run; just skip preview
        print(f"[Preview] Skipping preview: {e}")
        gallery_paths = []

    status_lines = ["✅ PDF generated."]
    if email:
        try:
            ok, msg = send_pdf_via_email(output_pdf)
            status_lines.append(("✅ " if ok else "⚠️ ") + msg)
        except Exception as e:
            status_lines.append(f"⚠️ Email skipped: {e}")
    if slack:
        try:
            ok, msg = post_to_slack(output_pdf)
            status_lines.append(("✅ " if ok else "⚠️ ") + msg)
        except Exception as e:
            status_lines.append(f"⚠️ Slack skipped: {e}")
    if webhook:
        try:
            ok, msg = post_webhook_message(os.getenv("WEBHOOK_URL"), output_pdf)
            status_lines.append(("✅ " if ok else "⚠️ ") + msg)
        except Exception as e:
            status_lines.append(f"⚠️ Webhook skipped: {e}")

    return df, "\n".join(status_lines), output_pdf, gallery_paths


with gr.Blocks(title="PDF Generator Interface") as demo:
    gr.Markdown("PDF Product Sheet Generator - Nested{Loop}")

    with gr.Row():
        use_dummy = gr.Checkbox(label="Use example file", value=False)
        file_input = gr.File(label="Upload Excel File", file_types=[".xlsx"], file_count="single")
    with gr.Row():
        email_box = gr.Checkbox(label="Send Email")
        slack_box = gr.Checkbox(label="Post to Slack")
        webhook_box = gr.Checkbox(label="Trigger Webhook")

    preview = gr.Dataframe(label="Excel Preview")
    status = gr.Textbox(label="Status", lines=6)
    download = gr.File(label="Download PDF")
    image_preview = gr.Gallery(label="PDF Preview Pages")

    generate_btn = gr.Button("Generate PDF")

    generate_btn.click(
        fn=process_excel,
        inputs=[file_input, email_box, slack_box, webhook_box, use_dummy],
        outputs=[preview, status, download, image_preview],
    )


if __name__ == "__main__":
    demo.launch()

