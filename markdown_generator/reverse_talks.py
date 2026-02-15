# coding: utf-8

# # Reverse Talks markdown generator for academicpages
#
# Takes markdown files with YAML front matter from the _talks directory and converts them back to a TSV file.
# This is the reverse process of talks.py

import pandas as pd
import os
import re
import yaml


def extract_yaml_and_content(file_path):
    """Extract YAML front matter and content from markdown file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by --- to separate YAML front matter
    parts = content.split("---")
    if len(parts) >= 3:
        yaml_str = parts[1]
        body = "---".join(parts[2:]).strip()
    else:
        return None, None

    try:
        yaml_data = yaml.safe_load(yaml_str)
    except:
        return None, None

    return yaml_data, body


def extract_talk_url(text):
    """Extract talk URL from [More information here](url) pattern."""
    match = re.search(r"\[More information here\]\(([^)]+)\)", text)
    if match:
        url = match.group(1)
        # Remove the link from text
        text = re.sub(r"\[More information here\]\([^)]+\)", "", text).strip()
        return url, text
    return "", text


def reverse_html_escape(text):
    """Reverse HTML escaping."""
    if isinstance(text, str):
        text = text.replace("&amp;", "&")
        text = text.replace("&quot;", '"')
        text = text.replace("&apos;", "'")
        return text
    return text


def main():
    talks_dir = "../_talks"

    if not os.path.exists(talks_dir):
        print(f"Error: {talks_dir} directory not found")
        return

    talks_data = []

    # Get all markdown files from _talks directory
    for filename in sorted(os.listdir(talks_dir)):
        if filename.endswith(".md"):
            file_path = os.path.join(talks_dir, filename)

            yaml_data, body = extract_yaml_and_content(file_path)
            if yaml_data is None:
                print(f"Skipping {filename}: Could not parse YAML")
                continue

            # Extract url_slug from filename (remove date prefix and .md extension)
            # Filename format: YYYY-MM-DD-slug.md or YYYY-slug.md
            name_without_ext = filename[:-3]  # Remove .md

            # Try to extract date prefix (YYYY-MM-DD or YYYY format)
            date_match = re.match(r"(\d{4}-\d{2}-\d{2}|\d{4})-(.*)", name_without_ext)
            if date_match:
                url_slug = date_match.group(2)
            else:
                url_slug = name_without_ext

            # Extract fields from YAML
            title = yaml_data.get("title", "")
            talk_type = yaml_data.get("type", "Talk")
            venue = yaml_data.get("venue", "")
            date = yaml_data.get("date", "")
            location = yaml_data.get("location", "")

            # Extract talk_url from body
            talk_url, description = extract_talk_url(body)

            # Reverse HTML escaping in description
            description = reverse_html_escape(description)

            # Convert date to string if it's a date object
            if date:
                date = str(date)

            talks_data.append(
                {
                    "title": title,
                    "type": talk_type,
                    "url_slug": url_slug,
                    "venue": venue,
                    "date": date,
                    "location": location,
                    "talk_url": talk_url,
                    "description": description,
                }
            )

    if not talks_data:
        print("No talks found")
        return

    # Create DataFrame
    df = pd.DataFrame(talks_data)

    # Write to TSV
    output_file = "talks.tsv"
    df.to_csv(output_file, sep="\t", index=False)
    print(f"Successfully created {output_file} with {len(talks_data)} talks")
    print("\nPreview:")
    print(df)


if __name__ == "__main__":
    main()
