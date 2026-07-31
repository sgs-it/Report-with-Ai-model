from pathlib import Path
import json
import os
import sys
from PIL import Image
from transformers import pipeline

ROOT = Path('d:/Dhaniyal/reports for training')
DATASET = ROOT / 'caption_dataset' / 'captions.jsonl'

ACTIVITY_CAPTIONS = [
    'Aeration for Grass',
    'After Hedge Trimming and Planter Bed Cleaning',
    'After Cleaning and Removal of Fallen Dry Leaves',
    'After Maintenance',
    'After Manual Watering',
    'After Mulch Top-Up',
    'After Removal of Dry and Overgrown Fronds',
    'After Removal of Dry Fronds',
    'After Replacing New Olive Tree',
    'After Replacement of Groundcovers (Wedelia)',
    'After Soil Cultivation',
    'Application of Compost',
    'Application of Inorganic Fertilizer',
    'Application of Micro Nutrients',
    'Application of NPK',
    'Application of Organic Compost',
    'Application of Pesticides',
    'Application of Urea',
    'Automated Irrigation',
    'Before Maintenance',
    'Cleaning After Lawn Mowing',
    'Cleaning After Pruning',
    'Cleaning After Weeding',
    'Cleaning and Removal of Fallen Dry Leaves',
    'Cleaning and Removal of Fallen Dry Leaves and Waste',
    'Cleaning and Removal of Waste',
    'Cleaning of Leaves',
    'Cleaning of Waste and Removal of Fallen Dry Leaves',
    'Dusting of Plants',
    'Dusting of Pot',
    'Fertilization',
    'Gap Filling of Groundcovers',
    'Green Shade Net Service for Plants',
    'Installation of Terram Sheet',
    'Irrigation Maintenance Check',
    'LAWN EDGING',
    'Lawn Edging',
    'LAWN MOWING',
    'Lawn Mowing',
    'Manual Watering',
    'Manual Watering After Planting',
    'Mulching',
    'Overseeding',
    'Pest Control Treatment',
    'Planting Seasonal Flowers',
    'Pruning',
    'Removal of Debris',
    'Removal of Dry Fronds',
    'Removal of Dry Leaves',
    'Removal of Dry Leaves and Manual Watering',
    'Removal of Dry Leaves and Weeds',
    'Removal of Existing Mulch',
    'Removal of Existing Olive Tree',
    'Removal of Existing Plants',
    'Removal of Existing Soil',
    'Removal of Fallen Dry Leaves',
    'Removal of Garbage',
    'Removal of Grass Clippings / Cleaning After Lawn Mowing',
    'Removal of Overgrown and Dry Fronds',
    'Removal of Overgrown and Dry Leaves',
    'Removal of Overgrown Leaves',
    'Removal of Waste and Plastics',
    'Removal of Weeds',
    'Removal and Disposal of Broken Crown',
    'Replacement of Groundcovers (Wedelia)',
    'Replacement of Seasonal Flowers (Petunia)',
    'Replacement of Seasonal Flowers (Vinca)',
    'SELECTIVE PRUNING',
    'Selective Pruning',
    'Soil Cultivation',
    'SPRINKLING OF WATER',
    'Sprinkling of Water',
    'Tree Pruning',
    'Trimming Activity',
    'Trimming and Shaping',
    'Washing of Plants',
    'Weeding',
    'Weeding and Removal of Dry Leaves',
]

print('Loading image classifier...')
classifier = pipeline('zero-shot-image-classification', model='openai/clip-vit-base-patch32', device=-1)


def load_examples(limit=20):
    if not DATASET.exists():
        return []
    rows = []
    with open(DATASET, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows[:limit]


def generate_caption(image_path):
    image = Image.open(image_path).convert('RGB')
    result = classifier(image, candidate_labels=ACTIVITY_CAPTIONS, top_k=1)
    if result:
        return result[0]['label']
    return 'After Maintenance'


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate a landscaping activity caption for an image file')
    parser.add_argument('image', help='path to an image file')
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        raise SystemExit(f'Image not found: {image_path}')

    caption = generate_caption(image_path)
    print('Generated caption:')
    print(caption)
