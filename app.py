<<<<<<< HEAD
import os


# Default to demo mode on Spaces; override locally with DEMO_MODE=0
os.environ.setdefault("DEMO_MODE", "1")

=======
>>>>>>> c1cdfcc6af1594e2e24ce705fd721fb65c2daa99
from src.interface import demo

<<<<<<< Updated upstream
demo.launch()
=======
if __name__ == "__main__":
    # Spaces sets PORT; default to 7860 locally
    port = int(os.getenv("PORT", "7860"))
    # Optional: disable SSR by setting SSR_MODE=0
    ssr_mode = os.getenv("SSR_MODE", "1") != "0"

    # Queue helps avoid overlapping PDF jobs
    demo.queue(default_concurrency_limit=1)
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        show_api=False,
        # Gradio's SSR flag varies by version; if you used it earlier:
        # ssr_mode
        # =ssr_mode,
    )
>>>>>>> Stashed changes
