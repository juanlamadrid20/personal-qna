#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urlparse
import os
import xml.etree.ElementTree as ET


def fetch_page(url):
    """Fetch the content of the page."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def extract_blog_content(html_content):
    """Extract the main content from the div with class 'rich-text-blog' using BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')

    main_content = soup.find('div', class_='rich-text-blog')

    if not main_content:
        raise ValueError("Could not find the div with class 'rich-text-blog'")

    # Remove all anchor tags
    for a_tag in main_content.find_all('a'):
        a_tag.decompose()

    return str(main_content)


def extract_doc_content(html_content):
    """Extract the main content from the div with class 'rich-text-blog' using BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')

    main_content = soup.find('div', itemprop='articleBody')

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


def get_output_filename_from_url(url, content_type='blogs'):
    """Extract the last path from the URL and use it as the filename."""
    parsed_url = urlparse(url)
    filename = parsed_url.path.strip('/').split('/')[-1] or 'output'

    # Add 'content/blogs' to the start of the filename
    return os.path.join('../content', content_type, f"{filename}.md")


def main():
    extract_docs()
    extract_blogs()


def extract_blogs():
    with open("/Users/jlamadrid/dev/blogs/personal-qna/util/urls.txt", "r") as file:
        urls = file.read().splitlines()

    for url in urls:
        try:
            html_content = fetch_page(url)
            main_html_content = extract_blog_content(html_content)
            markdown_content = convert_html_to_markdown(main_html_content)

            output_filename = get_output_filename_from_url(url, content_type='blogs')

            with open(output_filename, "w", encoding="utf-8") as md_file:
                md_file.write(markdown_content)

            print(f"Markdown file saved as '{output_filename}'")

        except Exception as e:
            print(f"An error occurred while handling '{url}': {e}")


def extract_docs():

    # Fetch the XML content from sitemap
    response = requests.get("https://docs.databricks.com/en/doc-sitemap.xml")
    root = ET.fromstring(response.content)
    # Find all 'loc' elements (URLs) in the XML
    urls = [loc.text for loc in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    print(f"{len(urls)} Databricks documentation pages found")

    # Let's take only the first 100 documentation pages to make this demo faster:
    urls = urls[:3500]

    for url in urls:
        try:
            html_content = fetch_page(url)
            main_html_content = extract_doc_content(html_content)
            markdown_content = convert_html_to_markdown(main_html_content)

            output_filename = get_output_filename_from_url(url, content_type='docs')

            with open(output_filename, "w", encoding="utf-8") as md_file:
                md_file.write(markdown_content)

            print(f"Markdown file saved as '{output_filename}'")

        except Exception as e:
            print(f"An error occurred while handling '{url}': {e}")


if __name__ == "__main__":
    main()
