import sqlite3
import logging


"""
Database structure:
Table with all keywords
Table with all parties
Table with single keyword analysis for one party on a specific date.
"""


class DataBase:
    def __init__(self):
        self.con = sqlite3.connect('kwa.db')

    def createDB(self, parties: list, keywords: list):
        self.con.execute("""
        CREATE TABLE IF NOT EXISTS keyword (
            id INTEGER PRIMARY KEY, 
            keyword CHARACTER(128) UNIQUE
        );
        """)
        self.con.execute("""
        CREATE TABLE IF NOT EXISTS party (
            id INTEGER PRIMARY KEY, 
            name CHARACTER(128) UNIQUE
        );
        """)
        self.con.execute("""
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY, 
            date DATE, 
            mentions INTEGER, 
            total INTEGER,
            party INTEGER,
            keyword INTEGER,
            FOREIGN KEY (party) REFERENCES party(id),
            FOREIGN KEY (keyword) REFERENCES keyword(id)
        );
        """)

        for party in parties:
            qs = self.con.execute("""
                    SELECT (name) FROM party WHERE name = (?);
                """, (party,))
            if qs.rowcount == 0:
                self.con.execute("""
                    INSERT INTO party (name) VALUES 
                        (?);
                    """, (party,))

        for keyword in keywords:
            qs = self.con.execute("""
                    SELECT (keyword) FROM keyword WHERE keyword = (?);
                """, (party,))
            if qs.rowcount == 0:
                self.con.execute("""
                    INSERT INTO keyword (keyword) VALUES
                        (?);
                    """, (keyword,))

        self.con.commit()  

    def saveTweets(self, keywordDict: dict, totals: dict):
        for keyword in keywordDict.keys():
            for party in keywordDict[keyword].keys():
                dates = keywordDict[keyword][party]
                for date in set(dates):
                    mentions = dates.count(date)
                    try:
                        total = totals[party].count(date)
                    except KeyError:
                        logging.error('Did not find total for date ' + date)
                        total = 0
                    qs = self.con.execute(
                        """
                        SELECT mentions, total 
                        FROM analysis 
                        WHERE 
                            date = (?) 
                        AND  
                            party = (SELECT id FROM party WHERE name = (?));
                        """,
                        [
                            date,
                            party
                        ]
                    )
                    # if no entry for this day exists yet
                    if qs.rowcount == 0:
                        self.con.execute(
                            """
                            INSERT INTO analysis (
                                date, 
                                mentions, 
                                total, 
                                party, 
                                keyword)
                            VALUES (
                                (?),
                                (?),
                                (?),
                                (SELECT id FROM party WHERE name = (?)),
                                (SELECT id FROM keyword WHERE keyword = (?))
                            );
                            """,
                            [
                                date,
                                mentions,
                                total,
                                party,
                                keyword
                            ]
                        )
                    # if there is already an entry for this day
                    else:
                        q_id, q_mentions, q_total = qs.fetchone()
                        mentions += q_mentions
                        total += q_total
                        self.con.execute(
                            """
                            UPDATE analysis
                            SET mentions = (?), total = (?)
                            WHERE id = (?);
                            """,
                            [
                                mentions,
                                total,
                                q_id
                            ]
                        )
        self.con.commit()

    def getKeywords(self) -> list:
        qs = self.con.execute(
            """
            SELECT keyword FROM keyword;
            """
        )
        return [keyword for (keyword, ) in qs]


    def getKeywordDetails(self, keyword: str) -> list:
        keywords = self.getKeywords()

        # make sure not some crap gets putten into the sql statement
        if keyword not in keywords:
            logging.error('Unknown keyword used for query, possibly prevented SQL-injection. Keyword is ' + keyword)
            raise ValueError

        qs = self.con.execute(
            """
            SELECT date, mentions, total, party
            FROM ((analysis 
            JOIN keyword 
            ON analysis.keyword = keyword.id)
            JOIN party
            ON analysis.party = party.id)
            WHERE keyword = (?)
            GROUP BY party
            ORDER BY date;
            """, keyword
        )
        print(qs)
        return [{
            'date': date,
            'mentions': mentions,
            'total': total,
            'party': party
        } for (date, mentions, total, party) in qs]

    def close(self):
        self.con.close()

        