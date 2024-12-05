# gradio_image_labelling

Simple gradio app to manually label images.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python gradio_app.py --output_file=annotations.json --image_root=./data_to_label --classes=plat_front,plat_back,porte_front,porte_back,unknown
```