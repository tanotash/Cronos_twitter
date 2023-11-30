import pytz
import time
from fake_headers import Headers
import logging
from selenium.common.exceptions import NoSuchElementException
from typing import Union
import re
from dateutil.parser import parse
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ChromeOptions, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from random import randint
import datetime
import sqlalchemy as sa
import os   
from dotenv import load_dotenv
load_dotenv()






logger = logging.getLogger(__name__)
format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(format)
logger.addHandler(ch)


def check_retry(retry):
    return retry <= 0

def wait_until_tweets_appear(driver) -> None:
    """Wait for tweet to appear. Helpful to work with the system facing
    slow internet connection issues
    """
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="cellInnerDiv"]')))
    except WebDriverException:
        logger.exception(
            "Tweets did not appear!, Try setting headless=False to see what is happening")

def scroll_down(driver) -> None:
    """Helps to scroll down web page"""
    try:
        body = driver.find_element(By.CSS_SELECTOR, 'body')
        for _ in range(randint(1, 3)):
            body.send_keys(Keys.PAGE_DOWN)
    except Exception as ex:
        logger.exception("Error at scroll_down method {}".format(ex))



def find_all_tweets(driver) -> list:
    """finds all tweets from the page"""
    try:
        return driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
    except Exception as ex:
        logger.exception(
            "Error at method fetch_all_tweets : {}".format(ex))
        return []
    
from typing import Union
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

def find_content(tweet) -> Union[str, None]:
    """
    Finds and returns the content of a tweet.
    Returns:
        The content of the tweet as a string, or None if the content cannot be found.
    """
    try:
        content_element = tweet.find_element(By.CSS_SELECTOR, 'div[lang]')
        return content_element.text
    except NoSuchElementException:
        return ""
    except Exception as ex:
        logger.exception("Error at method find_content : {}".format(ex))


def find_like(tweet) -> Union[int, None]:
    """finds the like of the tweet"""
    try:
        like_element = tweet.find_element(
            By.CSS_SELECTOR, '[data-testid="like"]')
        likes = like_element.get_attribute("aria-label")
        return int(re.search(r'\d+', likes).group(0))
    except Exception as ex:
        logger.exception("Error at method find_like : {}".format(ex))

def find_timestamp(tweet) -> Union[str, None]:
        """finds timestamp from the tweet"""
        try:
            timestamp = tweet.find_element(By.TAG_NAME,
                                           "time").get_attribute("datetime")
            posted_time = parse(timestamp).isoformat()
            return posted_time
        except Exception as ex:
            logger.exception("Error at method find_timestamp : {}".format(ex))

def find_external_link(tweet) -> Union[str, None]:
        """finds external link from the tweet"""
        try:
            card = tweet.find_element(
                By.CSS_SELECTOR, '[data-testid="card.wrapper"]')
            href = card.find_element(By.TAG_NAME, 'a')
            return href.get_attribute("href")

        except NoSuchElementException:
            return ""
        except Exception as ex:
            logger.exception(
                "Error at method find_external_link : {}".format(ex))

def find_shares(tweet) -> Union[int, str]:
    """finds shares from the tweet"""
    try:
        shares_element = tweet.find_element(
                By.CSS_SELECTOR, '[data-testid="retweet"]')
        shares = shares_element.get_attribute("aria-label")
        return int(re.search(r'\d+', shares).group(0))
    except Exception as ex:
        logger.exception("Error at method find_shares : {}".format(ex))
        return ""

def find_status(tweet) -> Union[list, tuple]:
    """finds status and link from the tweet"""
    try:
        anchor = tweet.find_element(
            By.CSS_SELECTOR, "a[aria-label][dir]")
        id = anchor.get_attribute("href").split("/")[-1]
        return id
    except Exception as ex:
        logger.exception("Error at method find_status : {}".format(ex))
        return []

def find_link(tweet) -> Union[list, tuple]:
    """finds status and link from the tweet"""
    try:
        anchor = tweet.find_element(
            By.CSS_SELECTOR, "a[aria-label][dir]")
        return anchor.get_attribute("href")
    except Exception as ex:
        logger.exception("Error at method find_status : {}".format(ex))
        return []

def find_autor(text) -> Union[list, tuple]:
    """finds autor from the link tweet"""
    try:
        anchor = text.split(sep='/')
        return anchor[3]
    except Exception as ex:
        logger.exception("Error at method find_autor : {}".format(ex))
        return []

def find_replies(tweet) -> Union[int, str]:
    """finds replies from the tweet"""
    try:
        replies_element = tweet.find_element(
            By.CSS_SELECTOR, '[data-testid="reply"]')
        replies = replies_element.get_attribute("aria-label")
        return int(re.search(r'\d+', replies).group(0))
    except Exception as ex:
        logger.exception("Error at method find_replies : {}".format(ex))
        return ""

    
def check_tweets_presence(tweet_list,retry):
    if len(tweet_list) <= 0:
        retry -= 1

def wait_until_completion(driver) -> None:
    """waits until the page have completed loading"""
    try:
        state = ""
        while state != "complete":
            time.sleep(randint(3, 8))
            state = driver.execute_script("return document.readyState")
    except Exception as ex:
        logger.exception('Error at wait_until_completion: {}'.format(ex))

def fetch_and_store_data(driver, user):
    """
    Fetches and stores data from tweets for a given user.

    Args:
        driver: The web driver used to interact with the web page.
        user: The username of the user whose tweets are being fetched.

    Returns:
        A dictionary containing the fetched tweet data.
    """

    
    posts_data = {}
    time.sleep(5)

    scroll_down(driver)


    all_ready_fetched_posts = []
    wait_until_completion(driver)
    wait_until_tweets_appear(driver)
    retry = 15 # retry 10 times if no tweets are found
    try:


        present_tweets = find_all_tweets(driver)
        check_tweets_presence(present_tweets,retry)
        all_ready_fetched_posts.append(present_tweets)

        while True:

            for tweet in present_tweets:
                autor = find_autor(find_link(tweet))            
                tweet_url = find_link(tweet)
                replies = find_replies(tweet)
                retweets = find_shares(tweet)
                status = find_status(tweet) 
                posted_time = find_timestamp(tweet)
                if posted_time is None:
                    posted_time = None
                else:
                    posted_time = datetime.datetime.strptime(posted_time, "%Y-%m-%dT%H:%M:%S%z")
                    posted_time = posted_time.astimezone(pytz.timezone('America/mexico_city'))

           
                content = str(find_content(tweet))
                likes = find_like(tweet)

                hashtags = re.findall(r"#(\w+)", str(content))
                mentions = re.findall(r"@(\w+)", str(content))
                link = find_external_link(tweet)

                posts_data[f'{user}_{status}'] = {
                    "tweet_id": f'{user}_{status}',
                    "id": status,
                    "username": autor,
                    "replies": replies,
                    "retweets": retweets,
                    "likes": likes,
                    "posted_time": posted_time,
                    "content": content,
                    "hashtags": hashtags,
                    "mentions": mentions,
                    "tweet_url": tweet_url,
                    "external_links": link
                }

            scroll_down(driver)
            wait_until_completion(driver)
            wait_until_tweets_appear(driver)
            present_tweets = find_all_tweets(driver)
            present_tweets = [post for post in present_tweets if post not in all_ready_fetched_posts]
            check_tweets_presence(present_tweets,retry)
            all_ready_fetched_posts.extend(present_tweets)
            if check_retry(retry) is True:
                break
            return posts_data

    except Exception as ex:
        logger.exception(
            "Error at method fetch_and_store_data : {}".format(ex))
        return ''
        


def cronos_fun(user, driver) -> pd.DataFrame:
    """
    Fetches and stores data from Twitter for a given user.

    Args:
        user (str): The Twitter username of the user.
        driver: The driver object used for web scraping.

    Returns:
        pd.DataFrame: A DataFrame containing the fetched data.
    """
 
    url = "https://twitter.com"
    #driver.execute_script("window.open('');")
    #driver.switch_to.window(driver.window_handles[1])
    driver.get(f'{url}/{user}')
    a = fetch_and_store_data(driver, user)


    a = pd.DataFrame(a)
    a = a.transpose()

    return a
    
def segundos_a_segundos_minutos_y_horas(segundos) -> str:
    """
    Converts seconds to hours, minutes, and seconds.

    Args:
        segundos (int): The number of seconds to convert.

    Returns:
        str: The converted time in the format "HH:MM:SS".
    """
    horas = int(segundos / 60 / 60)
    segundos -= horas*60*60
    minutos = int(segundos/60)
    segundos -= minutos*60
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    
from users import users

options = ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
header = Headers().generate()['User-Agent']
options.add_argument('--disable-notifications')
options.add_argument('--disable-cache')
options.add_argument('--disable-popup-blocking')
options.add_argument('--user-agent={}'.format(header))

driver = webdriver.Chrome(options=options)
url = "https://twitter.com"
driver.get(f'{url}/i/flow/login')

driver.implicitly_wait(10)
username = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]')))
username.send_keys(os.getenv('USER'))
username.send_keys(Keys.ENTER)

password = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="password"]')))
password.send_keys(os.getenv('PASSW'))
password.send_keys(Keys.ENTER)
time.sleep(5)

cronos = pd.DataFrame()
now = time.time()
     



for user in users:
    a = cronos_fun(user, driver=driver)
   
    cronos = pd.concat([cronos, a])

driver.quit()
print(f'tiempo trascurrido: {time.time() - now}')


cronos.dropna(subset=['posted_time'], inplace=True)
cronos['posted_time'] = pd.to_datetime(cronos['posted_time']).dt.tz_convert('America/cancun')
hoy =  datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/cancun'))
cronos['alive'] = (hoy - cronos['posted_time']).dt.seconds
cronos['alive'] = cronos['alive'].apply(segundos_a_segundos_minutos_y_horas)
cronos = cronos.reindex( columns=['tweet_id','username', 'replies', 'retweets', 'likes','alive', 'posted_time',
       'content', 'hashtags', 'mentions', 'tweet_url', 'external_links'])
cronos = cronos.reset_index(drop=True)
cronos['alive'] = cronos['alive'].astype(str)
cronos['content'] = cronos['content'].astype(str)
cronos['content'] = cronos['content'].str.replace('\n','')


engine = sa.create_engine(
    str(os.getenv("CONEXION")),
    echo=False,
)

cronos.to_sql('tweets', engine, if_exists='append', index=False)  

