#!/usr/bin/env python
# coding: utf-8

import os
from dotenv import load_dotenv
from openai import OpenAI
import sys
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

# load openai api key
env_success = load_dotenv('openai.env')
if not env_success:
    print('Failed to find environment file')

pdf_path = "imgs_combined_temp.pdf"

def convert_image(file_path, remove_old=True):
    new_extension = 'png'

    im = Image.open(file_path)

    original_format = os.path.splitext(file_path)[1]
    file_name = os.path.splitext(file_path)[0]

    out_path = f'{file_name}.{new_extension}'

    im.save(out_path)
    if remove_old:
        os.remove(file_path)

    return out_path


def list_dir_full(path):
    return [f'{path}/{file}' for file in os.listdir('../test-imgs')]

# load images
imgs = sys.argv[1:]
images = [Image.open(img) for img in imgs]

# combine images into a temporary pdf file    
images[0].save(pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:])

# start the ai client
client = OpenAI()

prompt = f"""You are a professional mathematician who adheres to the highest standards of accuracy and rigor. Your work is intended for publication, and mistakes are embarrassing.
I will give you a series of images containing handwritten text. The text may contain standard written English, mathematical formulae, or a mix of the two.
Generate LaTeX code to render the handwritten text you observe. Your LaTeX code should compile to a PDF containing a typeset version of the handwritten text you observe on the page.
Format the text in a manner that seems clear and professional. Do not alter, extend, or modify the text that appears on the page in any way. Mistakes are embarrassing.
Return LaTeX code only, no yapping.
"""

# put the pdf file in AI client for later use
file = client.files.create(
    file=open(pdf_path, "rb"),
    purpose="user_data"
)

# add file + prompt to the user input
user_input = [
    {
        "type": "input_file",
        "file_id": file.id,
    },
    {
        "type": "input_text",
        "text": prompt
    }
]

# run the ai client
response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {
            "role": "user",
            "content": user_input
        }
    ]
)

# retrieve the response tex code
output_tex = response.output[0].content[0].text

# clean up possible artifacts that will close the code to not compile
output_tex = output_tex.replace('```latex', '').replace('```', '')

# print it out
print(output_tex)
# clean up after ourselves before we exit
os.remove(pdf_path)