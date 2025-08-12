#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import sys
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
 

def get_form_selects(html):
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        print("Form tidak ditemukan di halaman tersebut.", file=sys.stderr)
        sys.exit(1)
    selects = form.find_all("select")
    result = []
    for select in selects:
        name = select.get("name")
        options = []
        for option in select.find_all("option"):
            label = option.text.strip()
            value = option.get("value", "").strip()
            options.append({"label": label, "value": value})
        if name:
            result.append({"name": name, "options": options})
    return result

def prompt_user_select(name, options):
    print(f"\nSelect {name}:")
    for i, opt in enumerate(options, start=1):
        print(f"  {i}. {opt['label']}")
    while True:
        choice = input(f"Pilih nomor (1-{len(options)}): ").strip()
        if not choice.isdigit():
            print("Input harus angka.")
            continue
        choice = int(choice)
        if 1 <= choice <= len(options):
            return options[choice -1]["value"]
        print("Nomor di luar jangkauan.")

def fetch_form(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error request halaman form: {e}", file=sys.stderr)
        sys.exit(1)
    return resp.text

def submit_form(url, data):
    try:
        resp = requests.post(url, data=data, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error saat submit form: {e}", file=sys.stderr)
        sys.exit(1)
    return resp.text

def parse_table(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        print("Tabel hasil tidak ditemukan atau pencarian tidak mengembalikan hasil.")
        return []

    rows = []
    for tr in table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
        if cols:
            rows.append(cols)
    return rows

# ----- AI  integration -----
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def call_gemini_api(prompt, data):
    context_text = "\n".join(["\t".join(row) for row in data])
    full_prompt = f"Context:\n{context_text}\nUser Prompt:\n{prompt}"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
        )
        return response.text
    except Exception as e:
        return f"Error saat memanggil Gemini API: {e}"

def run_ai_mode(data):
    print("\nMasuk ke mode AI. Ketik 'end' untuk selesai.")
    while True:
        prompt = input("AI Prompt > ").strip()
        if prompt.lower() == "end":
            print("Program selesai.")
            sys.exit()
        response = call_gemini_api(prompt, data)
        print(f"AI Response:\n{response}\n")

def main():
    url = input("Masukkan URL form: ").strip()
    html = fetch_form(url)

    selects = get_form_selects(html)
    if not selects:
        print("Tidak ditemukan elemen <select> dalam form.", file=sys.stderr)
        sys.exit(1)

    form_data = {}
    for select in selects:
        value = prompt_user_select(select["name"], select["options"])
        form_data[select["name"]] = value

    # Beberapa form butuh tombol submit, coba cek tombol submit untuk dikirim:
    soup = BeautifulSoup(html, "html.parser")
    submit_btn = soup.find("input", {"type": "submit"})
    if submit_btn and submit_btn.get("name"):
        form_data[submit_btn["name"]] = submit_btn.get("value", "Submit")

    print("\nMengirim data form:")
    for k,v in form_data.items():
        print(f"  {k}: {v}")

    result_html = submit_form(url, form_data)
    rows = parse_table(result_html)

    if not rows:
        print("Tidak ada data hasil pencarian yang ditemukan.")
        return

    print("\nHasil pencarian:")
    print(json.dumps(rows, indent=2, ensure_ascii=False))

    # Loop CLI untuk perintah AI / end
    while True:
        cmd = input("\nKetik 'commandAI' untuk masuk ke mode AI, atau 'end' untuk keluar: ").strip().lower()
        if cmd == "commandai":
            run_ai_mode(rows)
        elif cmd == "end":
            print("Program selesai.")
            break
        else:
            print("Perintah tidak dikenal. Ketik 'commandAI' atau 'end'.")

if __name__ == "__main__":
    main()
