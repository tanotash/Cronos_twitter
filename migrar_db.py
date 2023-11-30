import sqlalchemy as sa
import pandas as pd

engine = sa.create_engine(
    "postgresql+psycopg2://postgres:ashwin@localhost:5432/cronos",
    echo=False,
    )
df = pd.read_sql('tweets', engine,)


df = df.sort_values('posted_time').drop_duplicates(subset=['tweet_id'], keep='last')
df.to_sql('cronos', engine, if_exists='append', index=False)

meta = sa.MetaData()

twitter = sa.Table('tweets', meta)
twitter.drop(engine, checkfirst=True)
