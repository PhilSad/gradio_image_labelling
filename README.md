# gradio_image_labelling

Simple gradio app to manually label images.

![demo ui](assets/hotdog.png)


## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python gradio_app.py \
    --output_file=annotations.json \
    --image_root=./data_to_label/ \
    --classes=hotdog,not_hotdog
```