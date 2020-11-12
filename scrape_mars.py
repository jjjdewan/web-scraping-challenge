import pymongo
import requests
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import time



# DB Setup
# 

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars 


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless=False)


def scrape():
    browser = init_browser()
    
    #collection.drop()
    
    ########################################################
    # Nasa Mars news
    ########################################################
    
    news_url = 'https://mars.nasa.gov/news/'
    browser.visit(news_url)
    time.sleep(2)
    
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    
    article = news_soup.find("div", class_='list_text')
    news_title = article.find("div", class_="content_title").text
    news_para = article.find("div", class_ ="article_teaser_body").text
    

    ########################################################
    # JPL Mars Space Images - Featured Image
    ########################################################
    
    image_url_featured = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url_featured)
    time.sleep(2)
    
    html_image = browser.html
    # Parse HTML using BeautifulSoup() func
    #
    jpl_soup = BeautifulSoup(html_image, 'html.parser')

    # Find background-image url from style tag
    featured_image_url  =jpl_soup.find('article')['style'].replace('background-image: url(','').replace(');', '')[1:-1]

    # NASA JPL Url
    index_url = 'https://www.jpl.nasa.gov'

    # Concatenate website NASA JPL url with scrapped url for image
    #
    featured_image_url = index_url + featured_image_url
    featured_image_title = jpl_soup.find('h1', class_="media_feature_title").text.strip()
    
    
    ########################################################
    # Mars fact
    ########################################################
    mars_facts_url = 'https://space-facts.com/mars/'
    browser.visit(mars_facts_url)
    time.sleep(2)
    
    # Using pandas function read_html() to parse the url and format df
    mars_facts = pd.read_html(mars_facts_url)
    mars_facts_df = mars_facts[0]
    mars_facts_df.columns = ['Description','Value']
    mars_facts_df.set_index('Description', inplace=True)

    # Convert dataframe to html
    mars_fact_html = mars_facts_df.to_html(header=False, index=False)
    
    
    ########################################################
    # Mars Hemispheres
    ########################################################
    
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    
    browser.visit(hemispheres_url)
    time.sleep(3)
    
    hemispheres_html = browser.html
    mh_soup = BeautifulSoup(hemispheres_url,"html.parser")
    items = mh_soup.find_all('div', class_='item')
    hemisphere_image_urls = []
    hemispheres_main_url = 'https://astrogeology.usgs.gov'
    
    for i in items:
    # Store title
        title = i.find('h3').text
    
    # Get web link for full image
        partial_img_url = i.find('a', class_='itemLink product-item')['href']
    
    # Visit link that contains full image on Mars Hemispheres
    #
        browser.visit(hemispheres_main_url + partial_img_url)
    
    # Get html object of individual hemisphere information website
        individual_img_html = browser.html
    
    # Parse through the html with Beautiful Soup for each
    # individual hemisphere information
    #
        soup = BeautifulSoup(individual_img_html, 'html.parser')
    
    # Get full image source for reporting
    #
        img_url = hemispheres_main_url + soup.find('img', class_='wide-image')['src']
    
    # Create "hemisphere_image_urls" dictionary by using append() with
    # the retreived information in the for loop
    #
        hemisphere_image_urls.append({"title" : title, "img_url" : img_url})
    

    # Create data dictionary
    mars_data = {
		'news_title' : news_title,
		'summary': news_para,
        'featured_image': featured_image_url,
        'featured_image_title': featured_image_title,
        'fact_table': mars_fact_html,
		'hemisphere_image_urls': hemisphere_image_urls,
        'news_url': news_url,
        'jpl_url': image_url_featured,
        'fact_url': mars_facts_url,
        'hemisphere_url': hemispheres_url,
        }
    collection.insert(mars_data)


