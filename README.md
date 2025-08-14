# CLI Web Scraper with AI Integration

This project is a **CLI-based Python script** for web scraping and AI-assisted data interaction. It allows you to scrape tables from websites with HTML forms and query the scraped data using AI.

---

## Features

- Fetch and parse HTML forms from a given URL.
- Dynamically list `<select>` options for user selection in the CLI.
- Submit form data and scrape the resulting table.
- Display extracted data directly in the CLI in JSON format.
- Optional AI integration using **Google Gemini API** to query or analyze scraped data interactively.
- Works in both standard mode (form submission + table parsing) and AI-assisted mode.

---

## Requirements

- Python 3.8+
- Required Python packages:
  - `requests`
  - `beautifulsoup4`
  - `python-dotenv`
  - `google-genai` (for AI integration)
- `.env` file with your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```
