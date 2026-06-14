'''
Ellie Meredith
IS 303 - A07

Book Market Pipeline
This scrapes book data from books.toscrape.com, stores it in a SQLite
database (using Peewee ORM), analyzes prices and ratings with Pandas,
and produces a visualization.

Inputs:
- https://books.toscrape.com (3 pages of book listings)
  Each page contains 20 books with title, price, and star rating.

Processes:
- fetch_page(): sends HTTP GET request and returns parsed HTML
- scrape_books(): loops through 3 pages, extracts book data with
  BeautifulSoup, includs rate limiting between requests
- store_books(): saves scraped books to SQLite database using Peewee,
  skips duplicates
- analyze(): queries database, loads into Pandas DataFrame, runs
  groupby and prints summary statistics
- visualize(): creates and saves a bar chart of average price by rating
- main(): does the full pipeline in order

Outputs:
- Printed summary: total books, price range, average price by rating
- bar_chart.png: average price by star rating
- books.db: SQLite database which has all of the scraped books
'''

import requests
from bs4 import BeautifulSoup
from peewee import SqliteDatabase, Model, CharField, FloatField, IntegerField
import pandas as pd
import matplotlib.pyplot as plt
import time

# --- Database Setup ---

db = SqliteDatabase("books.db")

RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}


class Book(Model):
    title = CharField(unique=True)
    price = FloatField()
    rating = IntegerField()

    class Meta:
        database = db


# --- Pipeline Functions ---

def fetch_page(url):
    """Fetch a URL and return a BeautifulSoup object, or None if it fails."""
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, "html.parser")
    else:
        print(f"Failed to fetch {url}: status {response.status_code}")
        return None


def scrape_books(num_pages=3):
    """Scrape book data from multiple pages. Returns a list of dicts."""
    all_books = []

    for page in range(1, num_pages + 1):
        url = f"https://books.toscrape.com/catalogue/page-{page}.html"
        soup = fetch_page(url)

        if soup:
            articles = soup.find_all("article", class_="product_pod")

            for article in articles:
                title_tag = article.find("h3")
                price_tag = article.find("p", class_="price_color")
                rating_tag = article.find("p", class_="star-rating")

                if title_tag and price_tag and rating_tag:
                    title = title_tag.find("a")["title"]
                    price = float(price_tag.text[2:])

                    rating_class = rating_tag.get("class", [])
                    rating_word = rating_class[1] if len(rating_class) > 1 else "One"
                    rating = RATING_MAP.get(rating_word, 1)

                    all_books.append({
                        "title": title,
                        "price": price,
                        "rating": rating
                    })

            print(f"Page {page}: scraped {len(articles)} books")

        if page < num_pages:
            time.sleep(1)

    return all_books


def store_books(book_list):
    """Store books in the database. Skips duplicates by title."""
    stored = 0
    skipped = 0

    for data in book_list:
        exists = Book.select().where(Book.title == data["title"]).exists()
        if not exists:
            Book.create(
                title=data["title"],
                price=data["price"],
                rating=data["rating"]
            )
            stored += 1
        else:
            skipped += 1

    print(f"Stored {stored} new books ({skipped} duplicates skipped)")


def analyze():
    """Query the database, load into Pandas, and print summary findings."""
    query = Book.select()
    data = [{"title": b.title, "price": b.price, "rating": b.rating}
            for b in query]
    df = pd.DataFrame(data)

    print(f"\n=== Book Market Analysis ===")
    print(f"Total books in database: {len(df)}")
    print(f"Price range: ${df['price'].min():.2f} to ${df['price'].max():.2f}")
    print(f"Average price: ${df['price'].mean():.2f}")
    print(f"Median price: ${df['price'].median():.2f}")

    print(f"\n=== Average Price by Star Rating ===")
    rating_avg = df.groupby("rating")["price"].mean()
    for stars, avg in rating_avg.items():
        print(f"  {stars} star(s): ${avg:.2f}")

    print(f"\n=== Number of Books per Rating ===")
    rating_count = df.groupby("rating")["price"].count()
    for stars, count in rating_count.items():
        print(f"  {stars} star(s): {count} books")

    return df


def visualize(df):
    """Create and save a bar chart of average price by star rating."""
    rating_avg = df.groupby("rating")["price"].mean()

    rating_avg.plot(kind="bar", color="steelblue")
    plt.title("Average Book Price by Star Rating")
    plt.xlabel("Star Rating")
    plt.ylabel("Average Price (£)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("bar_chart.png")
    # plt.show()
    print("\nChart saved as bar_chart.png")


# --- Main Pipeline ---

def main():
    db.connect()
    db.create_tables([Book])

    print("Step 1: Scraping books.toscrape.com...")
    book_list = scrape_books(num_pages=3)

    print("\nStep 2: Storing in database...")
    store_books(book_list)

    print("\nStep 3: Analyzing data...")
    df = analyze()

    print("\nStep 4: Creating visualization...")
    visualize(df)

    db.close()
    print("\nPipeline complete!")


main()