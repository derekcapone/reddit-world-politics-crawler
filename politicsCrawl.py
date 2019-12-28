import praw
import yaml
import datetime
import mysql.connector

keywords = ["US ", "USA ", "America", "United States", "Trump",
            "Republican", "Democrat"]

def connectToReddit():
    """
    Gets config info from YAML file
    Connects to reddit
    Returns: reddit connection object
    """
    # get config info
    with open('config.yaml') as file:
        config_info = yaml.full_load(file)
    
    # retrieve config values
    client_i = config_info['client_i']
    client_s = config_info['client_s']
    pw = config_info['pw']
    ua = config_info['ua']
    user = config_info['user']
    
    reddit = praw.Reddit(client_id=client_i,
                     client_secret=client_s, password=pw,
                     user_agent=ua, username=user)
    return reddit


def findSubstring(sub, string):
    """
    Finds if substring is contained inside string
    Returns: True if substring is found, False if not found
    """
    res = string.find(sub)
    return (res != -1)


def findKeyword(string):
    """
    Finds if string is found in keywords
    Returns: True if string is found, False if not found
    """
    if(string == None):
        return False
    for word in keywords:
        if(findSubstring(word, string)):
            return True  # if word is found return True
    # return false if word is not found
    return False


def insertData(cursor, date_str, total, count):
    """
    Inserts customer name and address into customer table
    Uses cursor for database
    """
    sql = "INSERT INTO subredditdata (date, us, total) VALUES (%s, %s, %s)"
    val = (date_str, count, total)
    cursor.execute(sql, val)


def connectToDatabase(db_name):
    """
    Connects to database "db_name"
    Returns database, cursor to database
    USAGE: mydb, mycursor = connectToDatabase()
    """
    # get config info
    with open('config.yaml') as file:
        config_info = yaml.full_load(file)
    
    # connect to database using config info
    db = mysql.connector.connect(
        host=config_info['host'],
        user=config_info['username'],
        password=config_info['password'],
        database=db_name
    )
    return db, db.cursor()


def storeData(total, us):
    # connect to database
    mydb, mycursor = connectToDatabase("redditcrawler")
    
    # generate date string 
    dt = datetime.datetime.now()
    dt_str = dt.strftime("%d-%m-%Y")

    # store in database
    insertData(mycursor, dt_str, total, us)
    mydb.commit()


if __name__ == "__main__":
    # initiate connection to subreddit
    reddit = connectToReddit()
    subreddit = reddit.subreddit('worldpolitics')

    hot = subreddit.hot(limit=100)

    tot_count = 0
    us_count = 0

    for submission in hot:
        # check for keywords 
        if(findKeyword(submission.link_flair_text)):
            us_count += 1
        elif(findKeyword(submission.title)):
            us_count += 1
        
        # increment total count
        tot_count += 1

    # connect to database and store in table 
    storeData(tot_count, us_count)

