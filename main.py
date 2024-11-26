import requests
from bs4 import BeautifulSoup
import urllib.parse
from collections import deque
import json
import csv
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to fetch the HTML content of a page
def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

# Functions to extract specific content from the soup
def extract_headings(soup):
    return [h.text.strip() for i in range(1, 7) for h in soup.find_all(f'h{i}')]

def extract_paragraphs(soup):
    return [p.text.strip() for p in soup.find_all('p')]

def extract_lists(soup):
    return [li.text.strip() for ul in soup.find_all('ul') for li in ul.find_all('li')]

def extract_links(soup):
    return [a.get('href') for a in soup.find_all('a') if a.get('href')]

def extract_images(soup):
    return [img.get('src') for img in soup.find_all('img') if img.get('src')]

# Function to find and return all valid internal links on a page
def find_internal_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()

    for anchor in soup.find_all('a', href=True):
        href = anchor['href']
        full_url = urllib.parse.urljoin(base_url, href)  # Make absolute URL
        if base_url in full_url:  # Only include links within the same domain
            links.add(full_url)

    return links

# Function to extract all specified data from a page
def extract_data(html, page_name):
    soup = BeautifulSoup(html, 'html.parser')
    return {
        "page": [page_name],
        "Headings": extract_headings(soup),
        "Paragraphs": extract_paragraphs(soup),
        "Lists": extract_lists(soup),
        "Links": extract_links(soup),
        "Images": extract_images(soup),
    }

# Function to crawl the entire website and scrape data
def crawl_and_scrape(base_url):
    visited = set()  # Track visited URLs
    queue = deque([base_url])  # Use a queue for BFS
    all_data = []

    while queue:
        current_url = queue.popleft()
        if current_url in visited:
            continue
        
        print(f"Scraping: {current_url}")
        visited.add(current_url)

        html = fetch_html(current_url)
        if not html:
            print(f"Failed to fetch content for {current_url}. Skipping.")
            continue

        # Get the page name from the URL or use a default one
        page_name = current_url.split("/")[-1] if current_url != base_url else "home"

        # Extract data from the current page
        page_data = extract_data(html, page_name)
        all_data.append(page_data)

        # Find internal links and add them to the queue
        internal_links = find_internal_links(html, base_url)
        for link in internal_links:
            if link not in visited:
                queue.append(link)

    return all_data

# Function to crawl and scrape multiple websites
def crawl_and_scrape_multiple(urls):
    all_data = {}
    for base_url in urls:
        print(f"\nStarting to crawl and scrape: {base_url}")
        scraped_data = crawl_and_scrape(base_url)
        if scraped_data:
            all_data[base_url] = scraped_data
        else:
            print(f"No data scraped for {base_url}. Skipping.")
    return all_data

# Function to save data in JSON format
def save_to_json(data, filepath):
    with open(filepath, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data saved to {filepath} (JSON format)")

# Function to save data in CSV format
def save_to_csv(data, filepath):
    csv_data = []
    for page_data in data:
        for i in range(len(page_data["Headings"])):
            row = {
                "Page": page_data["page"][0],
                "Heading": page_data["Headings"][i] if i < len(page_data["Headings"]) else "",
                "Paragraph": page_data["Paragraphs"][i] if i < len(page_data["Paragraphs"]) else "",
                "List": page_data["Lists"][i] if i < len(page_data["Lists"]) else "",
                "Link": page_data["Links"][i] if i < len(page_data["Links"]) else "",
                "Image": page_data["Images"][i] if i < len(page_data["Images"]) else "",
            }
            csv_data.append(row)

    with open(filepath, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ["Page", "Heading", "Paragraph", "List", "Link", "Image"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    print(f"Data saved to {filepath} (CSV format)")

# Tkinter GUI for user input
def run_gui():
    def start_scraping():
        urls_text = urls_entry.get("1.0", "end").strip()
        urls = [url.strip() for url in urls_text.splitlines() if url.strip()]
        if not urls:
            messagebox.showerror("Error", "Please enter at least one URL.")
            return
        
        output_format = format_var.get()
        if output_format not in ('json', 'csv', 'both'):
            messagebox.showerror("Error", "Please select a valid format.")
            return
        
        save_path = filedialog.askdirectory(title="Select Save Location")
        if not save_path:
            messagebox.showerror("Error", "Please select a save location.")
            return

        print("\nStarting to crawl and scrape multiple websites...")
        all_data = crawl_and_scrape_multiple(urls)

        if not all_data:
            messagebox.showinfo("Info", "No data was scraped. Please check the URLs.")
            return

        for base_url, scraped_data in all_data.items():
            domain_name = urllib.parse.urlparse(base_url).netloc
            domain_name = domain_name.replace('www.', '').split('.')[0]
            
            if output_format == 'json':
                save_to_json(scraped_data, f"{save_path}/{domain_name}_data.json")
            elif output_format == 'csv':
                save_to_csv(scraped_data, f"{save_path}/{domain_name}_data.csv")
            elif output_format == 'both':
                save_to_json(scraped_data, f"{save_path}/{domain_name}_data.json")
                save_to_csv(scraped_data, f"{save_path}/{domain_name}_data.csv")

        messagebox.showinfo("Success", "Scraping completed successfully!")

    root = tk.Tk()
    root.title("Web Scraping Tool")

    tk.Label(root, text="Enter URLs (one per line):").grid(row=0, column=0, padx=10, pady=10)
    urls_entry = tk.Text(root, width=50, height=10)
    urls_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="Select Output Format:").grid(row=1, column=0, padx=10, pady=10)
    format_var = tk.StringVar(value="json")
    tk.Radiobutton(root, text="JSON", variable=format_var, value="json").grid(row=1, column=1, sticky='w')
    tk.Radiobutton(root, text="CSV", variable=format_var, value="csv").grid(row=2, column=1, sticky='w')
    tk.Radiobutton(root, text="Both", variable=format_var, value="both").grid(row=3, column=1, sticky='w')

    tk.Button(root, text="Start Scraping", command=start_scraping).grid(row=4, column=0, columnspan=2, pady=20)

    root.mainloop()

# Entry point of the program
if __name__ == "__main__":
    run_gui()
