"""
src/interface.py

Gradio UI for:
- PDF product sheet generator
- CSV → CSV mapper
- Template Editor (create/validate/save YAML mapping templates)
"""


import gradio as gr
import pandas as pd
import os
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
from .csvbot.editor import skeleton_template, load_template_text, validate_template_yaml, summarize_template, save_template_text
from .utils import demo_df as _demo_df, save_mapping, load_mapping, apply_transforms


load_dotenv()

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

_csv_registry = TemplateRegistry()
_csv_lookups = DatabaseLookups()


def _list_csv_templates():
    """Return all YAML files under templates/csv/ as string paths."""
    
    return [str(p) for p in Path("templates/csv").glob("*.y*ml")]

def _map_csv(input_file, template_path):
    """Map an uploaded CSV using the selected template; return previews + output path."""

    if not input_file or not template_path:
        return None, None, "Please upload a CSV and select a template."
    
    in_path = getattr(input_file, "name", None) or getattr(input_file, "path", None) or input_file
    df_in = read_csv_any(in_path)
    tmpl = _csv_registry.get(template_path)
    df_out = apply_template(df_in, tmpl, _csv_lookups)
    out_path = Path("/tmp/csv_mapper_output.csv")
    write_csv(df_out, out_path, quote_all=True)

    return df_in.head(20), df_out.head(20), str(out_path)

def demo_df() -> pd.DataFrame:
    """Small example DataFrame for demos/tests."""

    return _demo_df()

def process_excel(file, email, slack, webhook, use_dummy):
    """Read Excel, build PDF, optionally send via email/Slack/webhook; return UI outputs."""

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


# ----- UI ----- 


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
        lambda: gr.Dropdown.update(choices=_list_csv_templates()),
        outputs=csv_tmpl,
    )

with gr.Blocks() as tpl_tab:
    gr.Markdown("### Create / Edit CSV Mapping Templates")
    with gr.Row(equal_height=True):
        # Left column
        with gr.Column(scale=1, min_width=260):
            tpl_list = gr.Dropdown(choices=_list_csv_templates(), label="Existing templates")
            load_btn = gr.Button("Load")
            gr.Markdown("**New template**")
            new_name = gr.Textbox(label="Template name", value="my_template")
            new_btn = gr.Button("New skeleton")
            refresh_btn = gr.Button("Refresh list")
        # Middle column
        with gr.Column(scale=2, min_width=480):
            try:
                yaml_editor = gr.Code(language="yaml", label="Template YAML", lines=26)
            except Exception:
                yaml_editor = gr.Textbox(label="Template YAML", lines=26)
        # Right column
        with gr.Column(scale=1, min_width=260):
            validate_btn = gr.Button("Validate", variant="secondary")
            status_box = gr.Textbox(label="Status", lines=4)
            save_btn = gr.Button("Save", variant="primary")
            download_btn = gr.Button("Download YAML")
            sample_csv = gr.File(label="Sample CSV (optional)", file_types=[".csv"])
            cols_table = gr.Dataframe(label="Columns", interactive=False)

    # Wire actions for Template Editor
    load_btn.click(lambda p: load_template_text(p), inputs=tpl_list, outputs=yaml_editor)
    new_btn.click(lambda n: skeleton_template(n), inputs=new_name, outputs=yaml_editor)
    refresh_btn.click(lambda: gr.Dropdown.update(choices=_list_csv_templates()), outputs=tpl_list)

    def _validate(txt):
        """Return human message + a summary table of the template."""

        ok, msg, _ = validate_template_yaml(txt)
        summary = summarize_template(txt)

        return (msg, summary)

    validate_btn.click(_validate, inputs=yaml_editor, outputs=[status_box, cols_table])

    def _save_and_refresh(txt):
        """Save YAML to disk then refresh the dropdown list."""

        ok, msg, path = save_template_text(txt)

        # Refresh drowpdown

        return msg, gr.Dropdown.update(choices=_list_csv_templates())

    save_btn.click(_save_and_refresh, inputs=yaml_editor, outputs=[status_box, tpl_list])

    download_btn.click(
        lambda txt: (Path("/tmp") / "template.yaml").write_text(txt, encoding="utf-8") or str(Path("/tmp") / "template.yaml"),
        inputs=yaml_editor,
        outputs=gr.File(),
    )

    # Show columns from a sample CSV
    def _show_cols(f):
        """Show column names from a sample CSV (helps when writing map rules)."""

        if not f:
            return None
        
        df = read_csv_any(getattr(f, "name", f))

        return pd.DataFrame({"column": list(df.columns)})

    sample_csv.change(_show_cols, inputs=sample_csv, outputs=cols_table)

# Single tab bar for the app
demo = gr.TabbedInterface(
    [pdf_tab, csv_tab, tpl_tab],
    ["PDF Generator", "CSV Mapper", "Template Editor"],
    title="Automation Workbench"
)


if __name__ == "__main__":
    demo.launch()
