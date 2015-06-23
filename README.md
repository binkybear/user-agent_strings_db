#User Agent Srings DB Scraper

This is a python script which will scrape two web sources and combine them into sqlite3 and json file.

I couldn't find a simple database to sort by crawler, OS, or version type so that's why I worte this.
I'm also learning python and gave me a good opportunity to practice.  It's not the best script but it
does the job.

## Screenshot

![Viewing the database](http://i.imgur.com/Ffy8LwUh.png)

*Screenshot of database on OSX using SQLProSQLite*

## Requirements

Python 2.7+
BeautifulSoup4
User_agents

## Installation

Using either pip or easy_install:

```bash
easy_install user_agents
easy_install beautifulsoup4
```

## Running
```bash
python uadown.py
```