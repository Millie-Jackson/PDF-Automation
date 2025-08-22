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
from pathlib import Path
from src.run_generators import generate_pdf_from_excel
from src.sender import send_pdf_via_email
from src.slack import post_to_slack
from src.webhook import post_webhook_message
from .csvbot.templates import TemplateRegistry
from .csvbot.lookup import DatabaseLookups
from .csvbot.mapper import apply_template
from .csvbot.io import read_csv_any, write_csv
from .utils import demo_df as _demo_df, save_mapping, load_mapping, apply_transforms


load_dotenv()

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

_csv_registry = TemplateRegistry()
_csv_lookups = DatabaseLookups()


def _list_csv_templates():
    
    return [str(p) for p in Path("templates/csv").glob("*.y*ml")]

def _map_csv(input_file, template_path):

    if not input_file or not template_path:
        return None, None, "Please upload a CSV and select a template."
    
    df_in = read_csv_any(getattr(input_file, "name", input_file))
    tmpl = _csv_registry.get(template_path)
    df_out = apply_template(df_in, tmpl, _csv_lookups)
    out_path = Path("/tmp/csv_mapper_output.csv")
    write_csv(df_out, out_path, quote_all=True)

    return df_in.head(20), df_out.head(20), str(out_path)


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


with gr.Blocks() as pdf_tab:
    # Top 3 columns
    with gr.Row(equal_height=True):
        # Left column
        with gr.Column(scale=1, min_width=260):
            use_dummy = gr.Checkbox(label="Use example file", value=False)
            gr.Markdown("**Options**")
            email_box = gr.Checkbox(label="Send Email")
            slack_box = gr.Checkbox(label="Post to Slack")
            webhook_box = gr.Checkbox(label="Trigger Webhook")
        # Middle column
        with gr.Column(scale=1, min_width=260):
            file_input = gr.File(label="Upload Excel File", file_types=[".xlsx"], file_count="single")
        # RIght column
        with gr.Column(scale=1, min_width=260):
            generate_btn = gr.Button("Generate PDF")
            status = gr.Textbox(label="Status", lines=6)
            download = gr.File(label="Download PDF")

    preview = gr.Dataframe(label="Excel Preview")
    image_preview = gr.Gallery(label="PDF Preview Pages")
    generate_btn.click(
        fn=process_excel,
        inputs=[file_input, email_box, slack_box, webhook_box, use_dummy],
        outputs=[preview, status, download, image_preview],
    )

with gr.Blocks() as csv_tab:
    gr.Markdown("### CSV -> CSV Mapper")
    # Top 3 columns
    with gr.Row(equal_height=True):
        # Left column
        with gr.Column(scale=1, min_width=260):
            gr.Markdown("**Template**")
            csv_tmpl = gr.Dropdown(choices=_list_csv_templates(), label="Template", interactive=True)
            refresh_tmpl = gr.Button("Refresh templates")
        # Middle column
        with gr.Column(scale=1, min_width=260):
            csv_in = gr.File(label="Input CSV", file_types=[".csv"])   
        # Right column
        with gr.Column(scale=1, min_width=260):     
            csv_btn = gr.Button("Map CSV")  
            csv_out_file = gr.File(label="Download Output")
    # Previews
    with gr.Row():           
        csv_in_tbl = gr.Dataframe(label="Input (head)")
        csv_out_tbl = gr.Dataframe(label="Output (head)")
    
    csv_btn.click(
        _map_csv,
        inputs=[csv_in, csv_tmpl],
        outputs=[csv_in_tbl, csv_out_tbl, csv_out_file]
    )

    # Refresh template dropdown
    refresh_tmpl.click(
        lambda: gr.Dropdown.update(choices=_list_csv_templates),
        outputs=csv_tmpl
    )

demo = gr.TabbedInterface(
    [pdf_tab, csv_tab],
    ["PDF Generator", "CSV Mapper"],
    title="Automation Workbench"
)


if __name__ == "__main__":
    demo.launch()
