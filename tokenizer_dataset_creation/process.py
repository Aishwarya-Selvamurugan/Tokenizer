import os

input_folder = "txt"
output_folder = "wiki_data_final"
os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:
            
            text = ""
            for line in infile:
                line = line.strip()

                if line.startswith("TITLE:"):
                    continue  # Ignore title
                elif line.startswith("TEXT:"):
                    text = line.replace("TEXT:", "").strip()
                elif line.startswith("="):  # New article starts
                    if text:
                        flat_text = text.replace('\n', ' ').strip()
                        outfile.write(flat_text + "\n")
                    text = ""
                else:
                    text += " " + line

            # Final article (if not already written)
            if text:
                flat_text = text.replace('\n', ' ').strip()
                outfile.write(flat_text + "\n")

print(f"✅ Cleaned text-only articles saved to: {output_folder}/")
