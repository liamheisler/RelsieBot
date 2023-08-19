'''
Connect to and modify in house D
'''

# database packages
import sqlite3

# data analytics
import pandas as pd
import numpy as np

# python util
from pathlib import Path
from datetime import datetime, date

# logging
import logging
logger = logging.getLogger(__name__)

ROOT = Path(__file__).absolute().parent.parent

class RelsieDB:
    DB_LOCATION = ROOT / 'data' / 'db' / 'relsie.db'
    sheet_id = '1FX5RiuOkcgLPE5gyKae34Mpv7CkVkheCZJzA7InUrm4'

    gids = {
        'archived_loot': '89531371',
        'ulduar': '217967088',
        'togc': '2078549246',
        'icc': ''
    }

    available_tiers = ['togc', 'ulduar'] # as of mid august '23


    def __init__(self, db_location = None):
        logger.info("RelsieDB initialized!")
        if db_location is not None:
            self.connection = sqlite3.connect(db_location)
        else:
            self.connection = sqlite3.connect(self.DB_LOCATION)

        # get the cursor
        self.cur = self.connection.cursor()

    
    def update_archived_loot(self):
        # configure which sheet to pull from
        archived_loot_id = self.gids.get('archived_loot')

        # generate link to the sheet, form which data can be extracted
        link = f'https://docs.google.com/spreadsheets/d/{self.sheet_id}/export?gid={archived_loot_id}&format=csv'

        # extract data from the sheets link
        df = pd.read_csv(f"{link}", encoding='utf-8')

        # cleanup
        df.columns = df.iloc[0]
        df = df.iloc[1:, 3:]

        df = df[(df['Item Not Received Data'] != "#VALUE!") & (df['Item Not Received Data'].notnull())]

        # assign last udpated date to the data to current date
        df['last_updated'] = date.today()

        # write to the db table
        df.to_sql('archived_loot', self.connection, if_exists='replace')
        logger.info("Wrote archived_loot data to relsieDB")

        return True


    def update_prio(self, tier = None):
        if tier is not None:
            if tier in ['togc', 'ulduar', 'icc']:
                gid = self.gids.get(tier)

                link = f'https://docs.google.com/spreadsheets/d/{self.sheet_id}/export?gid={gid}&format=csv'

                df = pd.read_csv(f"{link}", encoding='utf-8')

                # Drop up to row n since the first rows are ugly and unneccessary
                df = df.copy().iloc[3:, 1:]

                num_cols = df.shape[1] # how many columns in our data?

                # build out the remaining column names for each player & assign columns
                new_col_names = [
                    'boss',
                    'item',
                    'blank1'
                ]
                numbers = [f"player_{num}" for num in list(np.arange(1, num_cols + 1 - len(new_col_names)))]
                df.columns = new_col_names + numbers
                df.drop(columns='blank1', inplace=True)

                # write to the db table
                df.to_sql(tier, self.connection, if_exists='replace')

                return True
            
            else:
                logger.info("Improper tier selected, could not write to DB")
        else:
            logger.info("No tier specified in update_prio, refreshing all!")
            for tier in self.available_tiers:
                gid = self.gids.get(tier)

                link = f'https://docs.google.com/spreadsheets/d/{self.sheet_id}/export?gid={gid}&format=csv'

                df = pd.read_csv(f"{link}", encoding='utf-8')

                # Drop up to row n since the first rows are ugly and unneccessary
                df = df.copy().iloc[3:, 1:]

                num_cols = df.shape[1] # how many columns in our data?

                # build out the remaining column names for each player & assign columns
                new_col_names = [
                    'boss',
                    'item',
                    'blank1'
                ]
                numbers = [f"player_{num}" for num in list(np.arange(1, num_cols + 1 - len(new_col_names)))]
                df.columns = new_col_names + numbers
                df.drop(columns='blank1', inplace=True)

                # write to the db table
                df.to_sql(tier, self.connection, if_exists='replace')

                return True

        
    def get_drops(self, tier = None, item = None):
        sql = ""
        if tier is not None:
            if tier in ['ulduar', 'togc', 'icc']:
                if item is not None:
                    if tier == "togc":
                        sql = f'SELECT * FROM archived_loot DB WHERE DB.NOTES IN ("{item} (Heroic)")'
                    else:
                        sql = f'SELECT * FROM archived_loot DB WHERE DB.NOTES IN ("{item}")'
                else:
                    sql = f'SELECT * FROM archived_loot'
                
                logger.info("Returning data from get_drops to calling function")
                return pd.read_sql(sql, con=self.connection)
            else:
                logger.info("Improper tier selected, could not write to DB")
        else:
            logger.info("Tier not specified, please specify one!")

    
    def get_prio(self, tier = None, item = None):
        sql = ""
        if tier is not None:
            if tier in ['ulduar', 'togc', 'icc']:
                if item is not None:
                    if tier == "togc":
                        sql = f'SELECT * FROM {tier} DB WHERE DB.item IN ("{item} (Heroic)")'
                    else:
                        sql = f'SELECT * FROM {tier} DB WHERE DB.item IN ("{item}")'
                else:
                    sql = f'SELECT * FROM {tier}'

                logger.info("Returning data from get_prio to calling function")
                return pd.read_sql(sql, con=self.connection)
            else:
                logger.info("Improper tier selected, could not write to DB")
        else:
            logger.info("Tier not specified, please specify one!")

    

    def close(self):
        self.connection.close()
    

db = RelsieDB()
db.update_archived_loot()
db.update_prio()