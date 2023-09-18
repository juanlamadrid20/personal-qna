import os
import streamlit as st
import openai
from langchain.document_loaders import NotionDirectoryLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# get the current directory
base_dir = os.path.dirname(os.path.realpath(__file__))

# Get two levels up
grandparent_dir = os.path.dirname(base_dir)

# Load OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Delete existing FAISS index if exists
faiss_index_path = os.path.join(grandparent_dir, 'faiss_index')

try:
    if os.path.exists(faiss_index_path):
        for file_name in os.listdir(faiss_index_path):
            file_path = os.path.join(faiss_index_path, file_name)
            os.remove(file_path)
except PermissionError:
    print(f"No permission to delete files in {faiss_index_path}. Please check the file permissions.")

# Load the Notion content located in the folder 'content/notion'
notion_loader = NotionDirectoryLoader(os.path.join(grandparent_dir, 'content', 'notion'))
notion_documents = notion_loader.load()

# Load the markdown content located in the folder 'content/blogs'
markdown_loader = DirectoryLoader(os.path.join(grandparent_dir, 'content', 'blogs'))
markdown_documents = markdown_loader.load()

# Combine both content sources
documents = notion_documents + markdown_documents

# Split the content into smaller chunks
markdown_splitter = RecursiveCharacterTextSplitter(
    separators=["#", "##", "###", "\\n\\n", "\\n", "."],
    chunk_size=1500,
    chunk_overlap=100
)
docs = markdown_splitter.split_documents(documents)

# Initialize OpenAI embedding model
embeddings = OpenAIEmbeddings()

# Convert all chunks into vectors embeddings using OpenAI embedding model
# Store all vectors in FAISS index and save to local folder 'faiss_index'
db = FAISS.from_documents(docs, embeddings)
db.save_local(faiss_index_path)

print('Local FAISS index has been successfully saved.')