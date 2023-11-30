import sqlalchemy as sa
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()

engine = sa.create_engine(
        str(os.getenv("CONEXION")),
        echo=False,
    )
df = pd.read_sql('tweets', engine,)


df = df.sort_values('posted_time').drop_duplicates(subset=['tweet_id'], keep='last')
df.to_sql('cronos', engine, if_exists='append', index=False)

meta = sa.MetaData()

twitter = sa.Table('tweets', meta)
twitter.drop(engine, checkfirst=True)
