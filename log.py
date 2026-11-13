import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv

url = "https://quotes.toscrape.com/login"

session = requests.session()

try:
    response = session.get(url, timeout=15)
    response.raise_for_status()

    print("Status code:", response.status_code)
    print("URL:",response.url)

except requests.RequestException as e:
    print("Error visiting page!", e)
    raise SystemExit

soup = BeautifulSoup(response.text, "html.parser")

form = soup.find("form")

if form is None:
    print("Login form not found")
    raise SystemExit

action = form.get("action")
method = form.get("method")

csrf_token = form.find(
    "input",
    {"name": "csrf_token"}
).get("value")

if csrf_token is None:
    print("CSRF token not found!")
    raise SystemExit


login_data = {
    "csrf_token": csrf_token,
    "username": "kofi",
    "password": "ama"
}

login_url = urljoin(url, action)

try:
    if method != "post":
        raise ValueError(
            f"Unexpected form method {method}"
        )

    login_response = session.post(
        login_url,
        data=login_data,
        timeout=15
    )

    login_response.raise_for_status()

    print("\nLogin status:", login_response.status_code)
    print("Final URL:", login_response.url)

    
except (requests.RequestException, ValueError) as e:
    print("Login request failed!", e)
    raise SystemExit

login_soup = BeautifulSoup(login_response.text, "html.parser")

logout_link = login_soup.find(
    "a",
    string=lambda text: text and "logout" in text.lower()
)

if not logout_link:
    print("Login could bot be verified!")
    print(login_soup.get_text(" ", strip=True))
    raise SystemExit

print("\nLogin successful!")



all_quotes = []

page = 1

while True:

    secure_url = f"https://quotes.toscrape.com/page/{page}"

    print(f"Scrapping page {page}")

    secure_response = session.get(secure_url, timeout=15)

    secure_response.raise_for_status()

    print("\nProtected page status:", secure_response.status_code)
    print("Protected page URL:", secure_response.url)

    secure_soup = BeautifulSoup(secure_response.text, "html.parser")

    quotes = secure_soup.find_all("div", class_="quote")

    if not quotes:
        print("No quotes available!")
        break

    for quote in quotes:
        author = quote.find("small", class_="author").get_text(strip=True)
        saying = quote.find("span", class_="text").get_text(strip=True)
        tags = ", ".join(tag.get_text(strip=True) for tag in quote.find("div", class_="tags").find_all("a", class_="tag"))

        quote_data = {
            "author": author,
            "saying": saying,
            "tags": tags
        }

        all_quotes.append(quote_data)

    page += 1

with open("man.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["author", "saying", "tags"])

    writer.writeheader()
    writer.writerows(all_quotes)

print("Quotes successfully saved to csv")
print(f"The quotes were {len(all_quotes)} in all")


print("\nSession cookies:")

for cookie in session.cookies:
    print(cookie.name, "=", "[REDACTED]")

print("\nScraping completed")