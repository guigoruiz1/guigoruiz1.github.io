# Reverse Publications markdown generator for AcademicPages
#
# Takes markdown files from the _publications directory and converts them back to a TSV file.
# This is the reverse process of publications.py

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

    # Extract commented citation if present
    citation_match = re.search(r'#\s*citation:\s*[\'"]([^\'"]+)[\'"]', yaml_str)
    if citation_match:
        yaml_data["citation"] = citation_match.group(1)

    return yaml_data, body


def reverse_html_escape(text):
    """Reverse HTML escaping."""
    if isinstance(text, str):
        text = text.replace("&amp;", "&")
        text = text.replace("&quot;", '"')
        text = text.replace("&apos;", "'")
        return text
    return text


def main():
    publications_dir = "../_publications"

    if not os.path.exists(publications_dir):
        print(f"Error: {publications_dir} directory not found")
        return

    publications_data = []

    # Get all markdown files from _publications directory
    for filename in sorted(os.listdir(publications_dir)):
        if filename.endswith(".md"):
            file_path = os.path.join(publications_dir, filename)

            yaml_data, body = extract_yaml_and_content(file_path)
            if yaml_data is None:
                print(f"Skipping {filename}: Could not parse YAML")
                continue

            # Extract url_slug and date from filename (YYYY-MM-DD-slug.md)
            name_without_ext = filename[:-3]  # Remove .md
            date_match = re.match(r"(\d{4}-\d{2}-\d{2})-(.*)", name_without_ext)

            if date_match:
                pub_date = date_match.group(1)
                url_slug = date_match.group(2)
            else:
                print(
                    f"Skipping {filename}: Could not extract date and slug from filename"
                )
                continue

            # Extract fields from YAML
            title = yaml_data.get("title", "")
            venue = yaml_data.get("venue", "")
            paper_url = yaml_data.get("paperurl", "")
            category = yaml_data.get("category", "manuscripts")
            citation = yaml_data.get("citation", "")

            # Body is the excerpt
            excerpt = body

            # Reverse HTML escaping
            venue = reverse_html_escape(venue)
            citation = reverse_html_escape(citation)
            excerpt = reverse_html_escape(excerpt)

            # Clean up excerpt - remove newlines and extra whitespace
            excerpt = " ".join(excerpt.split())

            publications_data.append(
                {
                    "pub_date": pub_date,
                    "title": title,
                    "venue": venue,
                    "excerpt": excerpt,
                    "citation": citation,
                    "url_slug": url_slug,
                    "paper_url": paper_url,
                    "slides_url": "",  # Not present in current markdown files
                    "category": category,
                }
            )

    if not publications_data:
        print("No publications found")
        return

    # Create DataFrame
    df = pd.DataFrame(publications_data)

    # Reorder columns to match expected format
    columns_order = [
        "pub_date",
        "title",
        "venue",
        "excerpt",
        "citation",
        "url_slug",
        "paper_url",
        "slides_url",
        "category",
    ]
    df = df[columns_order]

    # Write to TSV
    output_file = "publications.tsv"
    df.to_csv(output_file, sep="\t", index=False)
    print(
        f"Successfully created {output_file} with {len(publications_data)} publications"
    )
    print("\nPreview:")
    print(df)


if __name__ == "__main__":
    main()
