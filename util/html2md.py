#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urlparse
import os

def fetch_page(url):
    """Fetch the content of the page."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def extract_main_content(html_content):
    """Extract the main content from the div with class 'rich-text-blog' using BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')

    main_content = soup.find('div', class_='rich-text-blog')

    if not main_content:
        raise ValueError("Could not find the div with class 'rich-text-blog'")

    # Remove all anchor tags
    for a_tag in main_content.find_all('a'):
        a_tag.decompose()

    return str(main_content)


def convert_html_to_markdown(html_content):
    """Convert HTML content to Markdown using html2text."""
    converter = html2text.HTML2Text()
    converter.ignore_links = True
    return converter.handle(html_content)


def get_output_filename_from_url(url):
    """Extract the last path from the URL and use it as the filename."""
    parsed_url = urlparse(url)
    filename = parsed_url.path.strip('/').split('/')[-1] or 'output'

    # Add 'content/blogs' to the start of the filename
    return os.path.join('../content', 'blogs', f"{filename}.md")


def main():

    with open("/Users/jlamadrid/dev/blogs/personal-qna/util/urls.txt", "r") as file:
        urls = file.read().splitlines()

    for url in urls:
        try:
            html_content = fetch_page(url)
            main_html_content = extract_main_content(html_content)
            markdown_content = convert_html_to_markdown(main_html_content)

            output_filename = get_output_filename_from_url(url)

            with open(output_filename, "w", encoding="utf-8") as md_file:
                md_file.write(markdown_content)

            print(f"Markdown file saved as '{output_filename}'")

        except Exception as e:
            print(f"An error occurred while handling '{url}': {e}")


if __name__ == "__main__":
    main()
