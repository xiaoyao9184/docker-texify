import os
import sys

if "APP_PATH" in os.environ:
    os.chdir(os.environ["APP_PATH"])
    # fix sys.path for import
    sys.path.append(os.getcwd())

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1" # For some reason, transformers decided to use .isin for a simple op, which is not supported on MPS

import gradio as gr

import pypdfium2

from texify.inference import batch_inference
from texify.model.model import load_model
from texify.model.processor import load_processor
from texify.output import replace_katex_invalid
from PIL import Image

MAX_WIDTH = 800
MAX_HEIGHT = 1000

def load_model_cached():
    return load_model()

def load_processor_cached():
    return load_processor()

def infer_image(pil_image, bbox, temperature, model, processor):
    input_img = pil_image.crop(bbox)
    model_output = batch_inference([input_img], model, processor, temperature=temperature)
    return model_output[0]

def open_pdf(pdf_file):
    return pypdfium2.PdfDocument(pdf_file)

def count_pdf(pdf_file):
    doc = open_pdf(pdf_file)
    return len(doc)

def get_page_image(pdf_file, page_num, dpi=96):
    doc = open_pdf(pdf_file)
    renderer = doc.render(
        pypdfium2.PdfBitmap.to_pil,
        page_indices=[page_num - 1],
        scale=dpi / 72,
    )
    png = list(renderer)[0]
    png_image = png.convert("RGB")
    return png_image

def get_uploaded_image(in_file):
    return Image.open(in_file).convert("RGB")

def resize_image(pil_image):
    if pil_image is None:
        return
    pil_image.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)

def texify(img, box, temperature):
    img_pil = Image.fromarray(img).convert("RGB")

    bbox_list = []
    if box is not None and len(box[1]) > 0 and len(sections) > 0:
        for idx, ((x_start, y_start, x_end, y_end), _) in enumerate(sections):
            left = min(x_start, x_end)
            right = max(x_start, x_end)
            top = min(y_start, y_end)
            bottom = max(y_start, y_end)
            bbox_list.append((left, top, right, bottom))
    else:
        bbox_list = [(0, 0, img_pil.width, img_pil.height)]

    output = ""
    inferences = [infer_image(img_pil, bbox, temperature, model, processor) for bbox in bbox_list]
    for idx, inference in enumerate(reversed(inferences)):
        output += f"### {len(sections) - idx}\n"
        katex_markdown = replace_katex_invalid(inference)
        output += katex_markdown + "\n"
        output += "\n"
    return output

# ROI means Region Of Interest. It is the region where the user clicks
# to specify the location of the watermark.
ROI_coordinates = {
    'x_temp': 0,
    'y_temp': 0,
    'x_new': 0,
    'y_new': 0,
    'clicks': 0,
}

sections = []

def get_select_coordinates(img, evt: gr.SelectData):
    # update new coordinates
    ROI_coordinates['clicks'] += 1
    ROI_coordinates['x_temp'] = ROI_coordinates['x_new']
    ROI_coordinates['y_temp'] = ROI_coordinates['y_new']
    ROI_coordinates['x_new'] = evt.index[0]
    ROI_coordinates['y_new'] = evt.index[1]
    # compare start end coordinates
    x_start = ROI_coordinates['x_new'] if (ROI_coordinates['x_new'] < ROI_coordinates['x_temp']) else ROI_coordinates['x_temp']
    y_start = ROI_coordinates['y_new'] if (ROI_coordinates['y_new'] < ROI_coordinates['y_temp']) else ROI_coordinates['y_temp']
    x_end = ROI_coordinates['x_new'] if (ROI_coordinates['x_new'] > ROI_coordinates['x_temp']) else ROI_coordinates['x_temp']
    y_end = ROI_coordinates['y_new'] if (ROI_coordinates['y_new'] > ROI_coordinates['y_temp']) else ROI_coordinates['y_temp']
    if ROI_coordinates['clicks'] % 2 == 0:
        sections[len(sections) - 1] = ((x_start, y_start, x_end, y_end), f"Mask {len(sections)}")
        # both start and end point get
        return (img, sections)
    else:
        point_width = int(img.shape[0]*0.05)
        sections.append(((ROI_coordinates['x_new'], ROI_coordinates['y_new'],
                          ROI_coordinates['x_new'] + point_width, ROI_coordinates['y_new'] + point_width),
                        f"Click second point for Mask {len(sections) + 1}"))
        return (img, sections)

def del_select_coordinates(img, evt: gr.SelectData):
    del sections[evt.index]
    # recreate section names
    for i in range(len(sections)):
        sections[i] = (sections[i][0], f"Mask {i + 1}")

    # last section clicking second point not complete
    if ROI_coordinates['clicks'] % 2 != 0:
        if len(sections) == evt.index:
            # delete last section
            ROI_coordinates['clicks'] -= 1
        else:
            # recreate last section name for second point
            ROI_coordinates['clicks'] -= 2
            sections[len(sections) - 1] = (sections[len(sections) - 1][0], f"Click second point for Mask {len(sections) + 1}")
    else:
        ROI_coordinates['clicks'] -= 2

    return (img[0], sections)


model = load_model_cached()
processor = load_processor_cached()

with gr.Blocks(title="Texify") as demo:
    gr.Markdown("""
    After the model loads, upload an image or a pdf, then draw a box around the equation or text you want to OCR by clicking and dragging.
    Texify will convert it to Markdown with LaTeX math on the right.
    If you have already cropped your image, select "OCR image" in the sidebar instead.
    """)

    with gr.Row():
        with gr.Column():
            in_file = gr.File(label="PDF file or image:", file_types=[".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp"])

            in_num = gr.Slider(label="Page number", minimum=1, maximum=100, value=1, step=1)
            in_img = gr.Image(label="Select ROI of Image", type="numpy", sources=None)
            in_temperature = gr.Slider(label="Generation temperature", minimum=0.0, maximum=1.0, value=0.0, step=0.05)
            in_btn = gr.Button("OCR ROI")
        with gr.Column():
            gr.Markdown("""
            ### Usage tips
            - Don't make your boxes too small or too large.  See the examples and the video in the [README](https://github.com/vikParuchuri/texify) for more info.
            - Texify is sensitive to how you draw the box around the text you want to OCR. If you get bad results, try selecting a slightly different box, or splitting the box into multiple.
            - You can try changing the temperature value on the left if you don't get good results.  This controls how "creative" the model is.
            - Sometimes KaTeX won't be able to render an equation (red error text), but it will still be valid LaTeX.  You can copy the LaTeX and render it elsewhere.
            """)
            in_box = gr.AnnotatedImage(
                label="ROI",
                color_map={
                    "ROI of OCR": "#9987FF",
                    "Click second point for ROI": "#f44336"}
            )
            markdown_result = gr.Markdown(label="Markdown of results")

        def show_image(file, num=1):
            sections = []
            if file.endswith('.pdf'):
                count = count_pdf(file)
                img = get_page_image(file, num)
                # Resize to max bounds
                resize_image(img)
                return [
                    gr.update(visible=True, maximum=count),
                    gr.update(value=img)]
            else:
                img = get_uploaded_image(file)
                # Resize to max bounds
                resize_image(img)
                return [
                    gr.update(visible=False),
                    gr.update(value=img)]

        in_file.upload(
            fn=show_image,
            inputs=[in_file],
            outputs=[in_num, in_img],
        )
        in_num.change(
            fn=show_image,
            inputs=[in_file, in_num],
            outputs=[in_num, in_img],
        )
        in_img.select(
            fn=get_select_coordinates,
            inputs=[in_img],
            outputs=in_box
        )
        in_box.select(
            fn=del_select_coordinates,
            inputs=in_box,
            outputs=in_box
        )
        in_btn.click(
            fn=texify,
            inputs=[in_img, in_box, in_temperature],
            outputs=[markdown_result]
        )

demo.launch()
