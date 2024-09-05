# Steam-Review-Scraper
Ever wanted to download all the reviews for a Steam game? The API given by Steam is great, but for larger games... I found that it misses a majority of the reviews. Other scrapers run into performance and memory issues when it comes to large games with over 100,000 reviews. Is there a solution? This is an alright bet!

Using the landing page for a game, we can utilize the built in filters to cycle through each day or hour. This structure allows this program to include a save feature (more below) and through time filtration we can avoid all memory related issues! Using this program I was able to get 99.7% of reviews for both No Man's Sky and Cyberpunk 2077, two gargantuanly popular games. The remaining .3% likely came from my bug fixes/troubleshooting or unavoidable errors from Steam themselves.

The program has two phases:
    1. The page is loaded with all the necessary filters and scrolls down as much as it can.
    2. All the loaded reviews are stored in a reviews vector. Then it cycles to the next day until the present.

When the program is scrolling, closing the web page will save all currently stored reviews. When the script is loaded again, you will return to the last seen webpage. Ideally, no reviews are double counted. During the data cleaning process, I would check just to make sure. I'm 99.7% sure that no reviews are left behind.

Anyway, that's all! Enjoy scraping to your heart's content!
 
# Sample
Included in this folder is an example of a Steam web scrape in an Excel file for the game "Mr. Saitou". This is a good example of how your data will look after being fully scraped.
The game is precious but unpopular, making it a great test for the program. Hit the run button to get all reviews from 8/27/24 to today!

## Requirements
You'll need to install the following libraries before beginning this project:
- Selenium
- OpenPyXL
- Pandas
- webdriver_manager.chrome
- time, datetime, and dateutil
