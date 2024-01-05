
<h1 align="center"> Twitter-scrapper and Dash</h1>

scrapping project that searches information about users to put into a dashboard by dash library, makes filter about a time living by tweet, uses a PostgreSQL DB to store this data, the project is split by 3 scripts

- scrapper.py that makes the scrapper in Twitter, this script uses a list of user and environment os variables to the Twitter credentials, this needs to put in a cronjobs to scrap every shot time to scrap the recent information
- dash_tweets.py that consults in real time a DB of PostgreSQL to show a DataFrame about the Twitter scrapper
- migrar_db.py Migrates tweets data from the ***'Main'*** table to the ***'History'*** table in the database. this script like the first one needs to run in cronjobs at midnight to start the new day or by the filter used in dash_tweets.py to show the information

To run this repository 

  `git clone https://github.com/tanotash/Cronos_twitter.git`
  
  `cd Cronos_twitter`
  
  `pip install -r requirements.txt`
  
  to run scrapper 
  `python3 scrapper.py`

  to run dashboard
  `python3 dash_tweets.py`