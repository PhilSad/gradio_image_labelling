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
    return data, annotated_images

def main():
    args = parse_arguments()
    output_file = args.output_file
    image_root = args.image_root
    classes = args.classes.split(',')
    # shortcuts = args.shortcuts.split(',')

    # assert len(classes) == len(shortcuts), "Number of classes and shortcuts must be the same"

    images = collect_images(image_root)
    existing_data, annotated_images = load_existing_annotations(output_file)

    # Filter out images that are already annotated
    images_to_label = [img for img in images if img not in annotated_images]

    if not images_to_label:
        print("No images to label.")
        return

    with gr.Blocks() as demo:
        current_index = gr.State(value=0)
        data_state = gr.State(value=existing_data)
        with gr.Row():
            image_display = gr.Image(label="Image to classify", value=images_to_label[0], show_label=True, height=300, width=300)

        def classify_image(idx, data, label):
            image_path = images_to_label[idx]
            data.append({'path': image_path, 'label': label})
            with open(output_file, 'w') as f:
                json.dump(data, f)
            idx += 1
            if idx < len(images_to_label):
                next_image = images_to_label[idx]
                return next_image, idx, data
            else:
                return gr.update(value=None), idx, data

        with gr.Row():
            for cls in classes:
                btn = gr.Button(cls, variant='primary')
                btn.click(
                    fn=partial(classify_image, label=cls),
                    inputs=[current_index, data_state],
                    outputs=[image_display, current_index, data_state]
                )
            

    demo.launch()

if __name__ == '__main__':
    main()

# Run the script
# python gradio_app.py --output_file=annotations.json --image_root=primark_smol --classes=plat_front,plat_back,porte_front,porte_back,unknown
