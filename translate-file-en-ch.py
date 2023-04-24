import openai
import os
import random
import string
import re

openai.api_key = "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"

def translate(text):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Translate the following English text to Simplified Chinese and output the markdown formatted code:\n{text}\n---\nTranslation:",
        max_tokens=2048,
        temperature=0.7,
    )

    return response.choices[0].text.strip()

#def split_text_into_chunks(text):
#    chunks = []
#    current_chunk = ""
#    for paragraph in text.split("\n\n"):
#        if len(current_chunk) + len(paragraph) > 2048:
#            chunks.append(current_chunk.strip())
#            current_chunk = paragraph
#        else:
#            current_chunk += "\n\n" + paragraph
#    chunks.append(current_chunk.strip())
#    print(f"Chunks: {chunks}")  # Add this line to print chunks
#    return chunks

def split_text_into_chunks(text, max_length=4000, long_paragraph_length=500):
    def split_long_paragraph(paragraph, max_len):
        words = paragraph.split()
        parts = []
        current_part = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_len:
                current_length += len(word) + 1
                current_part.append(word)
            else:
                parts.append(' '.join(current_part))
                current_part = [word]
                current_length = len(word)
        
        if current_part:
            parts.append(' '.join(current_part))
        
        return parts

    text_chunks = []
    current_chunk = ""
    
    for paragraph in text.split("\n"):
        if len(paragraph) > long_paragraph_length:
            if current_chunk.strip():
                text_chunks.append(current_chunk.strip())
                current_chunk = ""
            
            long_paragraph_parts = split_long_paragraph(paragraph, long_paragraph_length)
            text_chunks.extend(long_paragraph_parts)
        else:
            if len(current_chunk) + len(paragraph) < max_length:
                current_chunk += paragraph + "\n"
            else:
                text_chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n"
    
    if current_chunk.strip():
        text_chunks.append(current_chunk.strip())
    
    return text_chunks

def translate_and_save_chunk(chunk, output_dir, input_file, chunk_number):
    print(f"Translating chunk {chunk_number}: {chunk}")  # Add this line to print the input chunk
    translated_text = translate(chunk)
    print(f"Translated chunk {chunk_number}: {translated_text}")  # Add this line to print the translated text
    output_file = os.path.join(output_dir, f"{os.path.splitext(input_file)[0]}_{chunk_number:04d}.txt")
    with open(output_file, 'w') as f:
        f.write(f"{translated_text}\n")
    return output_file

def get_chunk_number(filename):
    # Extract the chunk number from the filename if it follows the expected pattern
    match = re.search(r'_([0-9]+)\.txt', filename)
    return int(match.group(1)) if match else None

def merge_files(output_dir, input_file):
    output_files = [f for f in os.listdir(output_dir) if f.endswith(".txt") and not f.endswith("_merged.txt")]
    output_files = [f for f in output_files if get_chunk_number(f) is not None]  # Filter out files with invalid chunk numbers
    output_files.sort(key=get_chunk_number)  # Sort output files based on chunk_number

    print(f"Output files to be merged: {output_files}")  # Debug: print output files

    if len(output_files) == 0:
        print("Error: no output files found")
        return None

    merged_file = os.path.join(output_dir, f"{os.path.splitext(input_file)[0]}_translated.txt")
    translated_texts = []

    for file in output_files:
        with open(os.path.join(output_dir, file), 'r') as g:
            translated_text = g.read().strip()  # Read the entire content of the chunk
            print(f"Content of {file}: {translated_text}")  # Add this line to print the content of each file
            translated_texts.append(translated_text)    
            print(f"Appending {file} with content: {translated_text}")  # Debug: print appending file and its content
        os.remove(os.path.join(output_dir, file))

    with open(merged_file, 'w') as f:
        for translated_text in translated_texts:
            print(f"Translated_texts: {translated_texts}")  # Add this line to print translated_texts
            f.write(f"{translated_text}\n\n")  # Add an extra newline to separate paragraphs

    return merged_file


input_file = input("Enter the path to the input file: ")
output_dir = os.path.dirname(input_file)

with open(input_file, 'r') as f:
    input_text = f.read()

if len(input_text.strip()) == 0:
    print("Error: input text is empty")
else:
    chunks = split_text_into_chunks(input_text)

    output_files = []

    for i, chunk in enumerate(chunks):
        output_file = translate_and_save_chunk(chunk, output_dir, os.path.basename(input_file), i)
        output_files.append(output_file)
        print(f"Chunk {i+1}/{len(chunks)} translated and saved to {output_file}")

    merged_file = merge_files(output_dir, os.path.basename(input_file))

    if merged_file is None:
        print("Error: no output files found")
    elif os.path.getsize(merged_file) == 0:
        print("Error: output file is empty")
    else:
        with open(merged_file, 'r') as f:
            translated_text = f.read()
        output_text = translated_text.strip()
        # output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}_translated.txt")  # Remove this line
        with open(merged_file, 'w') as f:  # Use merged_file instead of output_file
            f.write(f"{output_text}\n")
        print(f"Translation saved to {merged_file}")  # Use merged_file instead of output_file
