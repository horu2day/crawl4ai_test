# Web Crawler to Markdown

This Python script is an asynchronous web crawler that fetches content from a specified URL, converts it into markdown format, and saves it to a local directory. It's designed to crawl an entire domain by following internal links and storing the content as readable markdown files.

## Features

- **Asynchronous Crawling:** Utilizes `asyncio` and `crawl4ai` for efficient, non-blocking web requests.
- **Markdown Conversion:** Automatically converts fetched web page content into clean markdown.
- **Structured Output:** Saves markdown files with a naming convention derived from the URL, ensuring organized storage.
- **Domain-Specific Traversal:** Follows internal links within the same domain to crawl an entire website section.
- **Error Handling:** Includes basic error handling for network requests and file operations.

## Requirements

- Python 3.7+
- `crawl4ai` library

## Installation

1. **Clone the repository (if applicable) or download the `main.py` file.**
2. **Install the required library:**

   ```bash
   pip install crawl4ai
   ```

## Usage

1. **Open `main.py`** in your preferred text editor.
2. **Modify `start_url`:** Change the `start_url` variable to the URL you wish to start crawling from.

   ```python
   start_url = "https://github.com/supabase/supabase-py" # Change this to your desired URL
   ```

3. **Modify `output_dir` (optional):** Change the `output_dir` variable to specify where the markdown files should be saved. By default, it's `output_markdowns`.

   ```python
   output_dir = "output_markdowns" # Change this if you want a different output directory
   ```

4. **Run the script:**

   ```bash
   python main.py
   ```

The script will start crawling the specified URL and save the converted markdown files into the `output_markdowns` directory (or your specified directory).

## Output Structure

All generated markdown files will be saved in the `output_markdowns/` directory (or the directory you specified). The file names are constructed from the domain and path of the crawled URL, ensuring uniqueness and easy identification.

Example:
`output_markdowns/github.com_supabase_supabase-py.md`
`output_markdowns/flet.dev_docs_.md`
