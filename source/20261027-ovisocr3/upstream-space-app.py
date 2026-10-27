import html
import logging
import os
from pathlib import Path

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
os.environ.setdefault("GRADIO_TEMP_DIR", str(Path(__file__).resolve().parent / "runtime/gradio-cache"))

import gradio as gr
from starlette.middleware import Middleware
from starlette.middleware.gzip import GZipMiddleware

from catalog import DEFAULTS, DOMAINS, ROOT, TASK_DOMAIN, build_prompt, load_cases
from documents import load_inputs, pdf_page_limit
from pipeline import execute
from rendering import pending_output
from presentation import DOMAIN_CHOICES, TASK_VIEWS, REGION_TASKS, JSON_TASKS, task_heading, status_html, list_json, input_summary
from region_selection import FULL_REGION, REGION_INPUT_TASKS, REGION_CACHE, region_image, selected_region, source_key
from region_inspector import inspector_payload, inspector_template
from source_preview import example_thumbnail, source_preview
from crosspage_view import CrossPageView, progress_html

gr.set_static_paths(paths=[ROOT / 'assets', ROOT / 'examples', REGION_CACHE])
CASES = load_cases()
TASK_EXAMPLE_DOMAINS = {"General OCR", "Key Information Extraction"}
FIRST = next((case for case in CASES if case["domain"] == "Document Parsing"), None)
INITIAL_DOMAIN = "Document Parsing"
INITIAL_TASK = FIRST["task"] if FIRST else "document_markdown"
EMPTY = pending_output(INITIAL_TASK)
CSS = (ROOT / "assets/workbench.css").read_text() + "\n" + (ROOT / "assets/region-inspector.css").read_text()
RESULT_JS = (ROOT / "assets/result.js").read_text()
LIST_JS = (ROOT / "assets/list-editor.js").read_text()
REGION_JS = (ROOT / "assets/region-geometry.js").read_text() + "\n" + (ROOT / "assets/region-editor.js").read_text()
APP_JS = (ROOT / "assets/workbench.js").read_text()
INSPECTOR_JS = (ROOT / "assets/region-inspector.js").read_text()


class StaticGZipMiddleware(GZipMiddleware):
    async def __call__(self, scope, receive, send):
        path = scope.get("path", "")
        static = path in {"/", "/theme.css", f"/gradio_api/file={ROOT / 'assets/mathjax.js'}"} or path.startswith(("/assets/", "/gradio_api/run/", "/gradio_api/api/"))
        if scope["type"] == "http" and static:
            await super().__call__(scope, receive, send)
        else:
            await self.app(scope, receive, send)


class PrivateImageCacheMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        path = scope.get('path', '')
        cached = scope['type'] == 'http' and any(
            path.startswith(f'/gradio_api/file={folder}/')
            for folder in (ROOT / 'examples', ROOT / 'assets', REGION_CACHE))

        async def send_cached(message):
            if cached and message['type'] == 'http.response.start' and message['status'] in (200, 304):
                headers = [(key, value) for key, value in message['headers'] if key.lower() != b'cache-control']
                headers.append((b'cache-control', b'private, max-age=86400'))
                message = {**message, 'headers': headers}
            await send(message)

        await self.app(scope, receive, send_cached)


APP_KWARGS = {"middleware": [Middleware(StaticGZipMiddleware, minimum_size=1024, compresslevel=4),
                             Middleware(PrivateImageCacheMiddleware)]}


class TaskDropdown(gr.Dropdown):
    is_template = True

    @classmethod
    def get_component_class_id(cls):
        return gr.Dropdown.get_component_class_id()

    def preprocess(self, payload):
        # A domain update can overtake a callback carrying the previous task.
        if payload in {task for tasks in DOMAINS.values() for _, task in tasks}:
            return payload
        return super().preprocess(payload)


def icon(name):
    return str(ROOT / "assets/icons" / f"{name}.svg")


def tool_button(name, label, attributes=""):
    return (f'<button type="button" class="tool-button" aria-label="{label}" title="{label}" {attributes}>'
            f'<img src="./gradio_api/file={icon(name)}" alt=""></button>')


def result_template():
    return ('<div class="result-shell"><div class="reader-toolbar">'
            '<span class="reader-state" aria-live="polite"></span><div class="reader-actions">'
            + tool_button('copy', 'Copy raw output', 'data-result-action="copy" disabled')
            + tool_button('maximize', 'Expand result', 'data-result-action="expand"')
            + '</div></div><div class="result-host"></div></div>')


def list_editor(value, label, item, elem_id):
    return gr.HTML(list_json(value), label=label, elem_id=elem_id,
                   editable=True, js_on_load=LIST_JS,
                   html_template=f'''<div class="list-editor" data-item="{item}">
                       <div class="list-heading"><span>{label}</span>
                           <button type="button" class="list-add" aria-label="Add {item}" title="Add {item}">
                               <img src="./gradio_api/file={icon('plus')}" alt="">
                           </button></div>
                       <div class="list-rows"></div>
                       <template><button type="button" class="list-remove">
                           <img src="./gradio_api/file={icon('trash-2')}" alt="">
                       </button></template>
                   </div>''')


def cases_for(domain, task=None):
    return [case for case in CASES if case["domain"] == domain
            and (domain not in TASK_EXAMPLE_DOMAINS or task is None or case["task"] == task)]


def case_paths(case):
    return [str(ROOT / path) for path in case["images"]] if case else []


def case_gallery(domain, task=None):
    return [(example_thumbnail(str(ROOT / case["images"][0])), case["title"]) for case in cases_for(domain, task)]


def preview_signature(task, paths, page):
    return {'identity': source_key(paths, page), 'drawing': task in REGION_INPUT_TASKS,
            'pair': task == 'crosspage_table',
            'gallery': [case['id'] for case in cases_for(TASK_DOMAIN[task], task)]}


def options_from_values(question, references, left, top, right, bottom, language, target, labels, keys, schema):
    references, labels, keys = [list_json(value) for value in (references, labels, keys)]
    return {"question": question, "references": references, "region": [left, top, right, bottom],
            "language": language, "target": target, "labels": labels, "keys": keys, "schema": schema}


def preview_prompt(task, *values):
    try:
        return build_prompt(task, options_from_values(*values))
    except (ValueError, TypeError) as exc:
        return f"Input required: {exc}"


def parameter_visibility(task):
    return [gr.update(visible=visible) for visible in (
        task in ("visual_question_answering", "position_aware_vqa"),
        task == "reference_grounding", task in ("region_ocr", "text_translation"),
        task == "text_translation", task == "image_classification", task == "kie_fields",
        task == "kie_schema", task == "crosspage_table",
    )]


def preview_files(paths, task, page, cache_files=None):
    drawing = task in REGION_INPUT_TASKS
    visibility = True if drawing else "hidden"
    empty = (gr.update(value=[], visible=not drawing), gr.HTML(image=None, visible=visibility))
    if not paths:
        return *empty, input_summary()
    try:
        prepared = source_preview(paths, task, page, drawing, cache_files)
        summary = prepared['summary']
        if drawing:
            return gr.update(value=[], visible=False), gr.HTML(
                image=prepared['region'], visible=True), summary
        return (gr.update(value=prepared['values'], visible=True, columns=2 if task == "crosspage_table" else 1,
                          preview=task != "crosspage_table", selected_index=None if task == "crosspage_table" else 0),
                gr.HTML(image=None, visible="hidden"), summary)
    except Exception as exc:
        message = str(exc) if isinstance(exc, ValueError) else "Unable to read this file. Select a valid image or PDF."
        return *empty, input_summary(error=message)


def pdf_control(paths, task):
    visible = bool(paths and any(path.lower().endswith('.pdf') for path in paths))
    try:
        maximum = pdf_page_limit(paths, task) or 100
    except Exception:
        maximum = 100
    return gr.update(visible=visible, maximum=maximum)


def case_values(case, domain):
    values = DEFAULTS | (case.get("options", {}) if case else {})
    return [gr.update(choices=DOMAINS[domain], value=case["task"] if case else DOMAINS[domain][0][1]),
            case_paths(case), 1, values["question"], list_json(values["references"]), *values["region"],
            values["language"], values["target"], list_json(values["labels"]), list_json(values["keys"]), values["schema"],
            case["benchmark"] if case else "", gr.HTML(expected=source_key(case_paths(case), 1), box=list(values["region"]))]


def on_domain(domain, paths=None, source=None):
    examples = cases_for(domain)
    values = case_values(examples[0] if examples else None, domain)
    if paths and not source:
        values = case_values(None, domain)
        values[1] = paths if domain == "Cross-Page Table Reconstruction" else paths[:1]
        values[-1] = gr.HTML(expected=source_key(values[1], values[2]), box=FULL_REGION)
    return [*values, case_gallery(domain, values[0]["value"])]


def on_example(domain, task, evt: gr.SelectData):
    return case_values(cases_for(domain, task)[int(evt.index)], domain)


def reset_results(task=INITIAL_TASK):
    return gr.HTML(value=pending_output(task), raw="", streaming=False), [], "", None, status_html(), gr.HTML(data=None), gr.update(value=None, visible=False), None


def reset_ui_results(task=INITIAL_TASK):
    base = reset_results(task)
    crosspage = task == 'crosspage_table'
    return (*base[:6], gr.HTML(value=progress_html() if crosspage else '', visible=crosspage),
            *[gr.HTML(value=pending_output('document_markdown', state=f'Page {number} / Waiting'), raw='', streaming=False) for number in (1, 2)],
            gr.update(selected='page-1' if crosspage else 'result'), *base[6:])


def task_presentation(task):
    return (task_heading(task), gr.update(label=TASK_VIEWS[task][1]),
            gr.update(visible=task in REGION_TASKS), gr.update(visible=task in JSON_TASKS),
            gr.update(visible=task == 'crosspage_table'), gr.update(visible=task == 'crosspage_table'))


def run_ui(task, paths, page, stage1, max_tokens, *values, inspector_cache_files=None, include_stages=False):
    stage_view = CrossPageView(stage1) if include_stages and task == 'crosspage_table' else None
    last_receipt = {}
    def output(base, update=None):
        if not include_stages:
            return base
        if update is None:
            extras = list(reset_ui_results(task)[6:10])
            if stage_view:
                extras[0] = gr.HTML(value=progress_html(state='running'), visible=True)
            return (*base[:6], *extras, *base[6:])
        extras = [gr.skip() for _ in range(4)]
        if stage_view:
            view = stage_view.update(update)
            extras = [gr.HTML(value=view['progress']) if view['progress'] is not None else gr.skip(),
                      *[gr.HTML(**{key: value for key, value in page.items()
                                   if key != 'value' or not page.get('streaming')}) if page else gr.skip()
                        for page in view['pages']],
                      gr.update(selected=view['selected']) if view['selected'] else gr.skip()]
            if not view['reconstruction']:
                base = (gr.skip(), base[1], gr.skip(), gr.skip(), *base[4:])
                if update.get('receipt', {}).get('status') == 'error':
                    base = (gr.HTML(value=pending_output(task, state='Reconstruction not started'), raw='', streaming=False), *base[1:])
        return (*base[:6], *extras, *base[6:])

    initial = (gr.HTML(value=pending_output(task, state='Waiting for page parsing' if stage_view else 'Preparing input'), raw="", streaming=False), [], "", None, status_html("Preparing input"), gr.HTML(data=None), gr.update(value=None, visible=False), None)
    yield output(initial)
    try:
        import inference as engine
        options = options_from_values(*values)
        for update in execute(paths, task, options, page, int(max_tokens), stage1, engine.infer_stream, engine.MODEL_SOURCE):
            last_receipt = update['receipt']
            parsing_page = stage_view and (last_receipt.get('calls') or [{}])[-1].get('stage') in {'page-1', 'page-2'}
            streaming = last_receipt.get('status') == 'running' and 'rendered' not in update
            if streaming:
                display = gr.HTML(raw=update['raw'], phase=update['status'], streaming=True)
            else:
                value = '' if parsing_page else update.get('rendered') or pending_output(task, update['raw'], update['status'])
                display = gr.HTML(value=value, raw=update['raw'], streaming=False)
            inspection = gr.skip()
            if 'source_images' in update and task in REGION_TASKS:
                try:
                    inspection = gr.HTML(data=inspector_payload(task, update.get('json'), update['source_images'],
                                                                paths, page, temp_files=inspector_cache_files))
                except Exception:
                    logging.getLogger(__name__).exception('Region inspector unavailable; preserving OCR results')
                    inspection = gr.HTML(data=None)
            yield output((display, update.get("overlays", gr.skip()),
                   update["raw"], update.get("json", gr.skip()), status_html(update["status"], update["receipt"], show_stages=not include_stages),
                   inspection, gr.update(value=update["download"], visible=True) if update.get("download") else gr.skip(), update["receipt"]), update)
    except Exception as exc:
        receipt = {**last_receipt, "status": "error", "error": str(exc)}
        yield output((gr.HTML(value=pending_output(task, state=f"Error: {exc}"), raw="", streaming=False), [], "", None, status_html(f"Error: {exc}"), gr.HTML(data=None), gr.update(value=None, visible=False), receipt), {'receipt': receipt})


def create_demo():
    initial_preview = source_preview(case_paths(FIRST), INITIAL_TASK, 1) if FIRST else None
    with gr.Blocks(title="OvisOCR3", analytics_enabled=False, delete_cache=(3600, 86400)) as demo:
        busy = gr.State(False)
        preview_state = gr.State(preview_signature(INITIAL_TASK, case_paths(FIRST), 1))
        gr.HTML(f'''<header id="brand"><div class="brand-lockup"><a class="brand-logo" href="https://huggingface.co/ATH-MaaS/OvisOCR3" target="_blank" rel="noopener"><img src="./gradio_api/file={ROOT / 'assets/ovis-logo.png'}" alt="Ovis"></a><h1><a href="https://huggingface.co/ATH-MaaS/OvisOCR3" target="_blank" rel="noopener">Ovis<span>OCR3</span></a></h1><span class="model-badge">0.8B</span></div><nav><a href="https://huggingface.co/ATH-MaaS/OvisOCR3" target="_blank" rel="noopener">Model</a><a href="https://arxiv.org/abs/2610.33066" target="_blank" rel="noopener" title="OvisOCR3 Technical Report (arXiv)">Technical Report</a><a href="https://github.com/AIDC-AI/Ovis" target="_blank" rel="noopener">GitHub</a></nav></header>''')
        domain = gr.Radio([choice for choice in DOMAIN_CHOICES if choice[1] in DOMAINS], value=INITIAL_DOMAIN,
                          label="Domain", show_label=False, container=False, elem_id="domain-nav")
        with gr.Row(elem_id="work-header"):
            heading = gr.HTML(task_heading(INITIAL_TASK), elem_id="task-heading", scale=10)
            gr.HTML('<div class="workbench-controls" data-icons="./gradio_api/file=' + str(ROOT / 'assets/icons') + '/">'
                    + tool_button('panel-left-close', 'Hide parameters', 'data-layout-action="rail" aria-pressed="false"')
                    + '<div class="view-segments" role="group" aria-label="Workspace view">'
                    + tool_button('columns-2', 'Compare source and result', 'data-layout-view="compare" aria-pressed="true"')
                    + tool_button('panel-left', 'Focus source', 'data-layout-view="source" aria-pressed="false"')
                    + tool_button('panel-right', 'Focus result', 'data-layout-view="result" aria-pressed="false"')
                    + '</div></div>', elem_id="workspace-tools", scale=0, min_width=156)
            stop = gr.Button("Stop", icon=icon("square"), interactive=False, scale=0, min_width=88, elem_id="stop-button")
            run = gr.Button("Run OCR", icon=icon("play"), variant="primary", scale=0, min_width=140, elem_id="run-button")
        gr.HTML('<div class="request-feedback" data-state="ready"><span class="request-dot"></span>'
                '<span class="request-phase">Ready</span><span class="request-elapsed" aria-label="Elapsed time"></span></div>',
                elem_id="request-feedback")
        selection_revision = gr.Textbox('', visible=False)
        selection_state = gr.HTML('', elem_id='selection-state')
        with gr.Row(elem_id="workspace"):
            with gr.Column(elem_id="task-panel", min_width=0):
                task = TaskDropdown(DOMAINS[INITIAL_DOMAIN], value=INITIAL_TASK, label="Task", elem_id="task-select")
                with gr.Group(visible=False) as question_group:
                    question = gr.Textbox(value=DEFAULTS["question"], label="Question", lines=2)
                with gr.Group(visible=False) as references_group:
                    references = list_editor(DEFAULTS["references"], "References", "reference", "reference-input")
                with gr.Group(visible=False, elem_id="region-controls") as region_group:
                    with gr.Row():
                        left = gr.Number(value=0, minimum=0, maximum=999, precision=0, label="Left", min_width=0)
                        top = gr.Number(value=0, minimum=0, maximum=999, precision=0, label="Top", min_width=0)
                    with gr.Row():
                        right = gr.Number(value=999, minimum=0, maximum=999, precision=0, label="Right", min_width=0)
                        bottom = gr.Number(value=999, minimum=0, maximum=999, precision=0, label="Bottom", min_width=0)
                with gr.Group(visible=False) as language_group:
                    language = gr.Dropdown(["English", "Chinese", "Japanese", "Korean", "French", "German", "Spanish", "Arabic"], value="English", allow_custom_value=True, label="Target language")
                with gr.Group(visible=False) as classification_group:
                    target = gr.Textbox(value=DEFAULTS["target"], label="Target description")
                    labels = list_editor(DEFAULTS["labels"], "Candidate labels", "label", "label-input")
                with gr.Group(visible=False) as fields_group:
                    keys = list_editor(DEFAULTS["keys"], "Fields", "field", "field-input")
                with gr.Group(visible=False) as schema_group:
                    schema = gr.Textbox(value=DEFAULTS["schema"], label="Output JSON template", lines=6, interactive=True, elem_classes=["mono-input"])
                with gr.Group(visible=False) as cross_group:
                    stage1 = gr.Radio([("Markdown", "document_markdown"), ("Structured", "document_structured")], value="document_markdown", label="Stage 1 / page parsing")
                gr.HTML('<div id="prompt-heading"><span class="section-label">Prompt</span><span>MODEL INPUT</span></div>')
                prompt_preview = gr.Textbox(value=build_prompt(INITIAL_TASK), lines=12, max_lines=18,
                                            interactive=False, buttons=["copy"], show_label=False, elem_id="prompt-preview")
                with gr.Accordion("Generation settings", open=False, elem_id="generation"):
                    max_tokens = gr.Slider(256, 16384, value=8192, step=256, label="Max tokens / stage")
            with gr.Column(elem_id="document-workspace", min_width=0):
                with gr.Row(elem_id="comparison"):
                    with gr.Column(scale=5, min_width=0, elem_id="input-panel"):
                        with gr.Row(elem_id="input-toolbar"):
                            gr.HTML(f'<div class="panel-label"><img src="./gradio_api/file={icon("file-text")}" alt=""><span>Source document</span></div>', scale=1)
                            upload = gr.UploadButton("Upload", icon=icon("upload"), file_count="multiple",
                                                     file_types=[".jpg", ".jpeg", ".png", ".webp", ".pdf"],
                                                     scale=0, min_width=76, elem_id="upload-button")
                            gr.HTML(tool_button('scan-search', 'Inspect source image', 'data-source-action="inspect"'),
                                    elem_id="inspect-source", scale=0, min_width=30)
                            swap = gr.Button("Swap page order", icon=icon("arrow-left-right"), visible=False,
                                             scale=0, min_width=30, elem_id="swap-button")
                            clear = gr.Button("Clear input", icon=icon("trash-2"), scale=0, min_width=30, elem_id="clear-button")
                        preview = gr.Gallery(value=initial_preview['values'] if initial_preview else [], label="Source pages", show_label=False, columns=1, rows=1,
                                             height=502, object_fit="contain", preview=True, selected_index=0,
                                             interactive=False, buttons=["fullscreen"], elem_id="input-preview")
                        region_editor = gr.HTML("", image=None, expected=source_key(case_paths(FIRST), 1), box=FULL_REGION, editable=True, visible="hidden",
                            elem_id="region-editor", js_on_load=REGION_JS,
                            html_template=f'''<div class="region-editor">
                                <div class="region-toolbar">
                                    <img src="./gradio_api/file={icon('rectangle-horizontal')}" alt="">
                                    <span class="region-coordinates"></span>
                                    <button type="button" class="region-reset" aria-label="Use full image" title="Use full image">
                                        <img src="./gradio_api/file={icon('scan-line')}" alt=""></button>
                                    <button type="button" class="region-fullscreen" aria-label="Fullscreen image" title="Fullscreen image">
                                        <img src="./gradio_api/file={icon('maximize')}" alt=""></button>
                                </div>
                                <div class="region-stage"><span class="region-empty">No image</span>
                                    <button type="button" class="region-retry tool-button" aria-label="Retry region image" title="Retry region image" hidden>
                                        <img src="./gradio_api/file={icon('rotate-cw')}" alt=""></button>
                                    <div class="region-picture" hidden><img class="region-image" alt="Source image" draggable="false">
                                        <div class="region-layer" tabindex="0" aria-label="Draw OCR region on source image">
                                            <div class="region-selection" hidden>
                                                <button type="button" class="region-handle nw" data-corner="nw" aria-label="Resize top-left" title="Resize top-left"></button>
                                                <button type="button" class="region-handle ne" data-corner="ne" aria-label="Resize top-right" title="Resize top-right"></button>
                                                <button type="button" class="region-handle sw" data-corner="sw" aria-label="Resize bottom-left" title="Resize bottom-left"></button>
                                                <button type="button" class="region-handle se" data-corner="se" aria-label="Resize bottom-right" title="Resize bottom-right"></button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>''')
                        source_info = gr.HTML(initial_preview['summary'] if initial_preview else input_summary(),
                                              elem_id="input-info")
                        files = gr.File(value=case_paths(FIRST), file_count="multiple", type="filepath", show_label=False,
                                        label="Image / PDF", file_types=[".jpg", ".jpeg", ".png", ".webp", ".pdf"], height=68, elem_id="input-upload")
                        page = gr.Number(value=1, precision=0, minimum=1, maximum=100, label="PDF page / first page", visible=False, elem_id="pdf-page")
                    gr.HTML('<div class="splitter" role="separator" aria-label="Resize source and result panels" '
                            'aria-orientation="vertical" aria-valuemin="30" aria-valuemax="70" aria-valuenow="46" tabindex="0"></div>',
                            elem_id="column-divider", scale=0, min_width=8)
                    with gr.Column(scale=6, min_width=0, elem_id="output-panel"):
                        progress = gr.HTML('', visible=False, elem_id='crosspage-progress')
                        with gr.Tabs(selected="result", elem_id="output-tabs") as output_tabs:
                            with gr.Tab('Page 1', id='page-1', visible=False) as page1_tab:
                                page1_result = gr.HTML('', raw='', streaming=False, phase='', elem_id='page-1-render', elem_classes=['page-render'],
                                                       html_template=result_template(), js_on_load=RESULT_JS)
                            with gr.Tab('Page 2', id='page-2', visible=False) as page2_tab:
                                page2_result = gr.HTML('', raw='', streaming=False, phase='', elem_id='page-2-render', elem_classes=['page-render'],
                                                       html_template=result_template(), js_on_load=RESULT_JS)
                            with gr.Tab(TASK_VIEWS[INITIAL_TASK][1], id="result") as result_tab:
                                rendered = gr.HTML(EMPTY, raw="", streaming=False, phase='', elem_id="result-render",
                                                   html_template=result_template(),
                                                   js_on_load=RESULT_JS)
                            with gr.Tab("Regions", id="regions", visible=False, elem_id="regions-tab") as regions_tab:
                                overlays = gr.Gallery(label="Detected regions", show_label=False, columns=1, height=570, object_fit="contain", interactive=False, buttons=["fullscreen"], elem_id="regions-preview")
                                inspector = gr.HTML("", data=None, elem_id="result-inspector",
                                                    html_template=inspector_template(), js_on_load=INSPECTOR_JS)
                            with gr.Tab("Raw", id="raw"):
                                raw = gr.Textbox(lines=28, max_lines=40, label="Raw model output", interactive=False,
                                                 buttons=["copy"], autoscroll=False, elem_id="raw-output")
                            with gr.Tab("JSON", id="json", visible=False) as json_tab:
                                parsed = gr.JSON(label="Parsed output", elem_id="parsed-output")
                with gr.Row(elem_id="status-row"):
                    status = gr.HTML(status_html(), elem_id="status", scale=1)
                    with gr.Column(scale=0, min_width=150, elem_id="download-slot"):
                        download = gr.DownloadButton("Download results", icon=icon("download"), value=None, visible=False, scale=0, min_width=150, elem_id="download-button")
                with gr.Accordion("Request details", open=False, elem_id="details"):
                    details = gr.JSON(label="Request & stage records")
                gr.HTML('<div id="examples-heading"><h3>Examples</h3><span>FROM THE TECHNICAL REPORT</span></div>')
                examples = gr.Gallery(value=case_gallery(INITIAL_DOMAIN), columns=4, rows=1, height=166,
                                      object_fit="cover", allow_preview=False, interactive=False,
                                      show_label=False, elem_id="case-gallery", buttons=[])
                source = gr.Markdown(FIRST["benchmark"] if FIRST else "", elem_id="source")

        params = [question, references, left, top, right, bottom, language, target, labels, keys, schema]
        groups = [question_group, references_group, region_group, language_group, classification_group, fields_group, schema_group, cross_group]
        results = [rendered, overlays, raw, parsed, status, inspector, progress, page1_result, page2_result, output_tabs, download, details]
        case_outputs = [task, files, page, *params, source, region_editor]
        def refresh_task(task, paths, page, *values, refresh_images=True):
            image_updates = (preview_files(paths, task, page, cache_files=region_editor.temp_files)
                             if refresh_images else (gr.skip(), gr.skip(), gr.skip()))
            return (*parameter_visibility(task), *task_presentation(task), *image_updates,
                    preview_prompt(task, *values), *reset_ui_results(task),
                    gr.update(visible=task == 'crosspage_table' and len(paths or []) == 2), pdf_control(paths, task),
                    preview_signature(task, paths, page))

        view_outputs = [*groups, heading, result_tab, regions_tab, json_tab, page1_tab, page2_tab, preview, region_editor, source_info, prompt_preview, *results, swap, page, preview_state]
        selection_outputs = list(dict.fromkeys([*case_outputs, examples, *view_outputs, selection_state, preview_state]))

        def select_inputs(domain_name, task_name, paths, page_number, source_name, running, revision,
                          previous_preview, evt: gr.EventData, *parameter_values):
            if running:
                return {component: gr.skip() for component in selection_outputs}
            target_id = getattr(evt.target, 'elem_id', None)
            if target_id == 'case-gallery':
                selected = cases_for(domain_name, task_name)[int(evt._data['index'])]
                values = case_values(selected, domain_name)
            elif target_id == 'task-select':
                candidates = cases_for(domain_name, task_name)
                if domain_name in TASK_EXAMPLE_DOMAINS and candidates and (source_name or not paths):
                    values = case_values(candidates[0], domain_name)
                else:
                    values = case_values(None, domain_name)
                    values[1:14] = [paths, page_number, *parameter_values]
                    values[14] = source_name
                    values[-1] = gr.HTML(expected=source_key(paths, page_number), box=list(parameter_values[2:6]))
                values[0] = gr.skip()
            else:
                values = on_domain(domain_name, paths, source_name)[:-1]
            selected_task = values[0].get('value', task_name)
            next_preview = preview_signature(selected_task, values[1], values[2])
            previous_preview = previous_preview or {}
            same_image = all(previous_preview.get(key) == next_preview[key] for key in ('identity', 'drawing', 'pair'))
            updates = dict(zip(case_outputs, values))
            view = dict(zip(view_outputs, refresh_task(selected_task, values[1], values[2], *values[3:14], refresh_images=not same_image)))
            if same_image:
                view[region_editor] = values[-1] if next_preview['drawing'] else gr.skip()
            else:
                view[region_editor] = gr.HTML(**(view[region_editor].constructor_args | values[-1].constructor_args))
            view[page] = {**view[page], 'value': values[2]}
            updates.update(view)
            if values[1] == paths:
                updates[files] = gr.skip()
            updates[examples] = (gr.skip() if previous_preview.get('gallery') == next_preview['gallery']
                                 else case_gallery(domain_name, selected_task))
            updates[preview_state] = next_preview
            updates[selection_state] = f'<span data-selection-revision="{html.escape(str(revision), quote=True)}"></span>'
            return updates

        gr.on([domain.input, task.select, examples.select], select_inputs,
              [domain, task, files, page, source, busy, selection_revision, preview_state, *params], selection_outputs,
              queue=False, trigger_mode='always_last', show_progress='hidden', api_name='select_domain',
              js="(...args) => {if (window.ovisSelection) args[6] = String(window.ovisSelection.start()); return args;}")

        coords = [left, top, right, bottom]

        swap_event = swap.click(lambda paths, running: (gr.skip(), gr.skip()) if running else (list(reversed(paths or [])), ''),
                   [files, busy], [files, source], queue=False, show_progress="hidden", api_name=False)
        file_upload_event = gr.on([files.upload, files.delete, files.clear],
                     lambda paths: ("", 1, *FULL_REGION, gr.HTML(expected=source_key(paths, 1), box=FULL_REGION)), files,
                     [source, page, *coords, region_editor], queue=False, show_progress="hidden", api_name=False)
        upload_event = upload.upload(lambda paths: (paths, "", 1, *FULL_REGION, gr.HTML(expected=source_key(paths, 1), box=FULL_REGION)), upload,
                      [files, source, page, *coords, region_editor], queue=False, show_progress="hidden", api_name=False)
        page_event = page.input(lambda paths, number: (*FULL_REGION, gr.HTML(expected=source_key(paths, number), box=FULL_REGION)), [files, page],
                   [*coords, region_editor], queue=False, show_progress="hidden", api_name=False)

        def apply_region(value, paths, task, page, running):
            if not running:
                try:
                    return selected_region(value, paths, task, page)
                except (ValueError, TypeError, KeyError):
                    pass
            return [gr.skip() for _ in coords]

        region_event = region_editor.input(apply_region, [region_editor, files, task, page, busy], coords,
                            queue=False, trigger_mode="always_last", show_progress="hidden", api_name=False)

        def refresh_parameters(task, *values):
            return preview_prompt(task, *values), *reset_ui_results(task), gr.HTML(box=list(values[2:6]))

        # Programmatic example updates refresh once after all parameters arrive.
        gr.on([component.input for component in params], refresh_parameters,
              [task, *params], [prompt_preview, *results, region_editor], queue=False,
              trigger_mode="always_last", show_progress="hidden", api_name=False)
        for action in [file_upload_event, upload_event, page_event, swap_event]:
            action.then(refresh_task, [task, files, page, *params], view_outputs,
                        queue=False, show_progress="hidden", api_name=False)
        for action in [region_event]:
            action.then(refresh_parameters, [task, *params], [prompt_preview, *results, region_editor],
                        queue=False, show_progress="hidden", api_name=False)
        stage1.input(reset_ui_results, task, results, queue=False, show_progress="hidden", api_name=False)
        max_tokens.input(reset_ui_results, task, results, queue=False, show_progress="hidden", api_name=False)
        controls = [run, stop, domain, task, files, clear, upload, page, stage1, max_tokens, *params, region_editor, swap]

        def set_running(running):
            return [gr.update(interactive=not running), gr.update(interactive=running),
                    *[gr.HTML(editable=not running) if component in (references, labels, keys, region_editor)
                      else gr.update(interactive=not running) for component in controls[2:]]]

        start = run.click(lambda task: (True, gr.update(selected='page-1' if task == 'crosspage_table' else 'result'),
                                       status_html('Queued / waiting for worker'), *set_running(True)),
                          inputs=task, outputs=[busy, output_tabs, status, *controls], queue=False, show_progress="hidden", api_name=False)
        def run_inspected(task, paths, page, stage1, max_tokens, *values):
            yield from run_ui(task, paths, page, stage1, max_tokens, *values, inspector_cache_files=inspector.temp_files, include_stages=True)

        event = start.then(run_inspected, [task, files, page, stage1, max_tokens, *params], results,
                           concurrency_limit=1, concurrency_id="model", show_progress="minimal", show_progress_on=[status], api_name="run")
        event.then(lambda: (False, *set_running(False)), outputs=[busy, *controls], queue=False, show_progress="hidden", api_name=False)
        def stop_ui(task, raw, receipt, parser):
            stage_updates = [gr.skip(), gr.skip(), gr.skip()]
            if task == 'crosspage_table':
                receipt = {**(receipt or {}), 'status': 'stopped'}
                stage_updates[0] = gr.HTML(value=progress_html(receipt))
                call = next(iter(reversed(receipt.get('calls', []))), {})
                if call.get('stage') in {'page-1', 'page-2'} and call.get('finish_reason') != 'stop':
                    number = int(call['stage'][-1])
                    stage_updates[number] = gr.HTML(value=pending_output(parser, call.get('text', ''), 'Stopped'), raw=call.get('text', ''), streaming=False)
            return (False, gr.HTML(value=pending_output(task, raw, 'Stopped'), raw=raw, streaming=False), status_html('Stopped'),
                    gr.HTML(data=None), *stage_updates, *set_running(False))
        stop.click(stop_ui, [task, raw, details, stage1], [busy, rendered, status, inspector, progress, page1_result, page2_result, *controls],
                   cancels=[event], queue=False, show_progress="hidden", api_name=False)
        clear_event = clear.click(lambda task: ([], [], "", *reset_ui_results(task), *FULL_REGION, gr.HTML(image=None, expected=None, box=FULL_REGION)), task,
                                  outputs=[files, preview, source, *results, *coords, region_editor], cancels=[event], queue=False, show_progress="hidden", api_name=False)
        clear_event.then(refresh_task, [task, files, page, *params], view_outputs,
                         queue=False, show_progress="hidden", api_name=False)
        demo.load(fn=None, js=APP_JS)
    return demo


demo = create_demo()


if __name__ == "__main__":
    import inference

    inference.load_model()
    port = int(os.getenv("PORT", "7860"))
    demo.queue(max_size=16, default_concurrency_limit=1).launch(
        server_name="0.0.0.0", server_port=port, share=False,
        ssr_mode=False,
        app_kwargs=APP_KWARGS,
        root_path=os.getenv("GRADIO_ROOT_PATH") or None,
        allowed_paths=[str(ROOT / "examples"), str(ROOT / "assets"), str(REGION_CACHE)],
        max_file_size="30mb", show_error=True, footer_links=[],
        theme=gr.themes.Base(primary_hue="blue", neutral_hue="gray", radius_size="sm",
                             font=["Arial", "sans-serif"], font_mono=["ui-monospace", "monospace"]), css=CSS,
    )
