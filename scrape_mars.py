from flask_pymongo import PyMongo
from splinter import Browser, browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser("chrome", **executable_path, headless = False)

def scrape():

    dict_data = {}
    browser = init_browser()

    url = "https://mars.nasa.gov/news/"
    jpl_url = "https://www.jpl.nasa.gov/images?search=&category=Mars"
    mars_url = "https://space-facts.com/mars/"
    hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

    browser.visit(url)
    time.sleep(1)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    titles_body_soup = soup.find_all("div", class_ = ("content_title", "article_teaser_body"))

    #display(len(titles_body_soup))
    title_list = []
    news_list = []
    for i,x in enumerate(titles_body_soup):
        if i % 2 == 0:
            news_list.append(x.text)
        else:
            title_list.append(x.text)
    #display(len(title_list))
    #display(len(news_list))
    #news list has extra line due to div content_title from nav bar element
    news_list = news_list[1:49]
    #display(len(news_list))

    browser.visit(jpl_url)
    time.sleep(.5)
    browser.find_by_css("img.BaseImage").click()
    browser.find_by_css("svg.IconExpand").click()
    jpl_html = browser.html
    soup0 = BeautifulSoup(jpl_html, "html.parser")
    featured_image_jpg = soup0.find_all("div", class_ ="BaseLightbox__slide__img")[0]("img")[0]["src"]

    browser.visit(mars_url)
    mars_table = pd.read_html(mars_url)
    planet_comparison_df = mars_table[1].set_index("Mars - Earth Comparison")
    #display(planet_comparison_df)   
    mars_facts = mars_table[0].rename(columns = ({0 : "Description", 1 : "Mars"})).set_index("Description")
    #display(mars_facts)
    mars_html = mars_facts.to_html()

    hemisphere_dict_list = []
    hemisphere_images_urls = {}
    browser.visit(hemi_url)
    time.sleep(.5)
    for x in range(4):
        browser.find_by_css("img.thumb")[x].click()
        browser.find_by_css("a.open-toggle").click()
        large_hemi_html = browser.html
        hemi_soup = BeautifulSoup(large_hemi_html, "html.parser")
        title= hemi_soup("h2", class_ = "title")[0].text
        hemisphere_images_urls["title"] = title.replace(" Enhanced", "")
        hemisphere_images_urls["img_url"] = hemi_soup("img", class_ = "wide-image")[0]["src"]
        hemisphere_dict_list.append(hemisphere_images_urls)
        browser.visit(hemi_url)
        hemisphere_images_urls = {}
    hemisphere_dict_list
    browser.quit()
    dict_data["article_title"]  = title_list[0]
    dict_data["news_list"] = news_list[0]
    dict_data["featured_image"] = featured_image_jpg
    dict_data["mars_table" ] = mars_html
    dict_data["hemisphere_dict_list"] = hemisphere_dict_list

    from pymongo import MongoClient
    mongo_conn=MongoClient('mongodb://localhost:27017')
    mars_db = mongo_conn["mars_db"]
    mars_coll = mars_db["mars"]
    mars_db.mars_coll.insert_one(dict_data)

    return dict_data

if __name__ == "__main__":
    scrape()