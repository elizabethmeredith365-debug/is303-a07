Analysis Write-Up
Dataset Description
I collected data from the website books.toscrape.com which is conveniently designed for web scarping. The pipeline collected 3 pages of listings (20 books per page) which totalled 60 books. Each book is stored in the database in 3 fields which are 1) a title (text), 2) price (a decimal numbe), and 3) a rating (an integer of 1 to 5 stars). The prices range from £10 to over £50.

Pipeline Description
It has 4 steps inside a main() function. Fetch_page() sends an HTTP GET request to every page and returns a BeautifulSoup object if the status code is 200. Then, scrape_books() loops through 3 pages, finds every article tag with class "product_pod", and it puls out the title, price, and star rating from each one. It waits 1 second between pages using time.sleep(1). Then, store_books() takes the list of dictionaries and creates a Peewee Book object for each, and it checks first whether a book with that title already exists so if there are any duplicates they are skipped. Then, analyze() queries all books from the database, loads them into a Pandas DataFrame, and runs groupby on the rating column to find the average price and count per star level. Then, visualize() produces a bar chart of avrage price (by rating) and saves it as bar_chart.png.

Findings
My analysis revealed that the star rating and price actually don’t have a very strong or clear correlation. The groupby results showed that the price varied across the rating levels, so some lower rated books were even more expensive than the higher rated ones. The average price was about £35 but ranged from about £10 to £50. 

Ethical Considerations
Since this site is meant for web scarping its’ robots.txt does not restrict access, and there are no terms of Service that restrict automated access. It’s ethical because no personal data was collected and it’s doesn’t contain any real user info. 


Limitations 
I think that biggest limit is sample size because I only scraped 3 pages of books, I think a larger sample size would’ve made it more accurate. If I had more time I might also add a category field to the database which would help with the groupby analysis. 
