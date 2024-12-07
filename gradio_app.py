import argparse
import os
import json
import gradio as gr
from functools import partial
import glob


def parse_arguments():
    parser = argparse.ArgumentParser(description='Image Labeling Tool')
    parser.add_argument('--output_file', type=str, required=True, help='Output JSON file')
    parser.add_argument('--image_root', type=str, required=True, help='Image folder root')
    parser.add_argument('--classes', type=str, required=True, help='Comma-separated list of classes')
    # parser.add_argument('--shortcuts', type=str, required=True, help='Comma-separated list of keyboard shortcuts')
    args = parser.parse_args()
    return args

def collect_images(image_root):
    # Collect images from subdirectories of subdirectories
    images = glob.glob(os.path.join(image_root, '**', '*.jpg'), recursive=True)
    images += glob.glob(os.path.join(image_root, '**', '*.jpeg'), recursive=True)

    images += glob.glob(os.path.join(image_root, '**', '*.png'), recursive=True)
    images += glob.glob(os.path.join(image_root, '**', '*.webp'), recursive=True)
    
    
    return images

def load_existing_annotations(output_file):
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            data = json.load(f)
        annotated_images = set([item['path'] for item in data])
    else:
        data = []
        annotated_images = set()
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    return annotated_images

def main():
    args = parse_arguments()
    output_file = args.output_file
    image_root = args.image_root
    classes = args.classes.split(',')

    images = collect_images(image_root)
    annotated_images = load_existing_annotations(output_file)
    # Filter out images that are already annotated
    images_to_label = [img for img in images]

    if not images_to_label:
        print("No images to label.")
        return



    def classify_image(idx, label):
        image_path = images_to_label[idx]
        with open(output_file, 'r') as f:
            data = json.load(f)
        data.append({'path': image_path, 'label': label})
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        idx += 1
        if idx < len(images_to_label):
            next_image = images_to_label[idx]
            return next_image, idx, f"{idx+1}/{len(images_to_label)}"
        else:
            return gr.update(value=None), idx, f"{idx+1}/{len(images_to_label)}"
    
    def undo_last_annotation(idx):
        with open(output_file, 'r') as f:
            data = json.load(f)
        if data:
            data.pop()
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        idx -= 1
        if idx >= 0:
            prev_image = images_to_label[idx]
            return prev_image, idx, f"{idx+1}/{len(images_to_label)}"
        else:
            return gr.update(value=None), idx, f"{idx+1}/{len(images_to_label)}"




    with gr.Blocks() as demo:
        current_index = gr.State(value=len(annotated_images))
        
        with gr.Row():
            count = gr.Label(f"{current_index.value+1}/{len(images_to_label)}", show_label=False)
        
        with gr.Row():
            image_display = gr.Image(label="Image to classify", value=images_to_label[len(annotated_images)], show_label=True, height=300, width=300)

        with gr.Row():
            for cls in classes:
                btn = gr.Button(cls, variant='primary')
                btn.click(
                    fn=partial(classify_image, label=cls),
                    inputs=[current_index],
                    outputs=[image_display, current_index, count]
                )
        with gr.Row():
            undo_btn = gr.Button("Undo", variant='secondary')
            undo_btn.click(
                fn=undo_last_annotation,
                inputs=[current_index],
                outputs=[image_display, current_index, count]
            )
        
            

    demo.launch()

if __name__ == '__main__':
    main()
