Image captioning workflow
========================

Files created:
- build_caption_dataset.py: extracts captions from the Word reports and writes a JSONL dataset.
- caption_from_image.py: generates a landscaping activity caption for a single image file using your approved activity labels.
- run_captioner.bat: one-click launcher for Windows.

How to use:
1. Put an image file somewhere on your machine.
2. Run:
   run_captioner.bat "C:\path\to\image.jpg"
3. The script will print one of the approved landscaping activity captions.

Notes:
- The script now uses a controlled list of landscaping activities such as:
  - Weeding and Removal of Dry Leaves
  - Lawn Mowing
  - Pruning
  - Manual Watering
  - After Maintenance
- This makes the output focus on the activity shown in the image, rather than a generic scene description.
