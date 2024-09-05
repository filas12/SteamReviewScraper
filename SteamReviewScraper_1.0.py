#Data Management Libraries
import pandas as pd
import openpyxl.workbook

#Web Scraping Libraries
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

#Time Based Libraries
import time
from datetime import datetime
from time import sleep
from dateutil import parser 


# Write game ID here. Ex: For a given steam link https://store.steampowered.com/app/628740/Mr_Saitou/, the ID is 628740
game_id = 628740

#Controls max number of reviews before going to hourly. We assume that the threshold is greater than the maximum hourly reviews for any game
#Set to a number that your computer can confortably handle.
reviewThreshold = 4000

# setup driver
template = 'https://store.steampowered.com/app/{}/Cyberpunk_2077/'
url = template.format(game_id)

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

driver.maximize_window()
driver.get(url)

#Useful variables
newFile = False
hourly = 0
filePath = f'Steam_Reviews_{game_id}.xlsx'
saveFile = f'Most_Recent_Timestamps/{game_id}_Timestamp.txt'
reviews = []

#Counters
reviewCounter = 0
earlyAccessLimit = 10
blankCoutdown = earlyAccessLimit
earlyAccessSave = 0

#Time Variables
midnight = int(time.time() - time.time() % 86400)
startTime = 1
endTime = midnight
            
#If the file doesn't exist, initializes new save file, new excel file, and uses game release date to initialize time. Else, reads from files to continue working.
#For early access games, we need to go backwards from this date.
def findInitialTimestamp():
    global earlyAccessSave, newFile
    
    try:
        with open(saveFile, "r") as f:
            saves = f.read()
            
        date = int(saves.split()[0])
        earlyAccessSave = int(saves.split()[1])
    

    except FileNotFoundError:
        

        newFile = True
    
        print(f"File not found. Will create the following file: {filePath} ")
        
        #Creates excel workbook
        wb = openpyxl.Workbook()
        wb.save(filePath)
        
        
        date = driver.find_element_by_xpath('//div[@class="date"]').text
        date = time.mktime(parser.parse(date.replace('Posted:', '')).timetuple())
        
        #'date', like 'midnight', is in UTC time.
        date = int(date - date % 86400)
        earlyAccessSave = date
        
    return date

#Finds number of reviews for a given date range
def howManyReviews():
    
    while True:
        sleep(2)    
        numReviews = driver.find_elements_by_xpath('//*[@id="user_reviews_filter_score"]/div/span[1]/b')
        if(len(numReviews) > 0) :
            numReviews = numReviews[0].text
            if numReviews == '':
                continue
            break
        
    
    numReviews = int(numReviews.replace(',', ''))
    return numReviews

#Called to take all currently displayed reviews and scrape their data     
def aquireData():
    
    recent = driver.find_element_by_xpath('//*[@id="Reviews_recent"]')
    cards = recent.find_elements_by_class_name('review_box')
    
    global reviewCounter
    global blankCoutdown
    
    for card in cards:
    
        reviewID = card.find_element_by_xpath('./div').get_attribute('id').replace('ReviewContentrecent', '')
        
        rating = card.find_element_by_xpath('.//*[@class="title ellipsis"]').text
    
        reviewerID = card.find_element_by_xpath('.//*[@class="avatar"]/a').get_attribute('href').split('/')[-2]
    
        if(startTime < earlyAccessSave):
            earlyAccess = True
        else:
            earlyAccess = False
        
        try:
            card.find_element_by_xpath('.//*[@class="receivedCompensation tooltip"]')
            free = True
        except Exception:
            free = False

        reviewContent = card.find_element_by_xpath('.//*[@class="content"]').get_attribute("textContent")
    
        posted = card.find_element_by_xpath('.//*[@class="postedDate"]').text.replace('POSTED: ', '')
    
        if posted.find(',') == -1:
            posted += f', {datetime.now().year}'

        #Steam can not display hours very rarely. This try command is neccesary unfortunatly. 
        try:
            hours = card.find_element_by_xpath('.//*[@class="hours ellipsis"]').text.split()[0]
        except Exception:
            hours = '0'
        
        helpful = card.find_element_by_xpath('.//*[@class="vote_info"]').text
        
        if helpful.find('helpful') == -1:
            helpful = '0'
        else:
            helpful = helpful.split()[0]
        #With the landing page, number of funny ratings are only shown if at least one person rates it helpful. We cannot accuratly find the number of funny ratings for all reviews.
        
        
        reviews.append([reviewID, reviewerID, rating, reviewContent, posted, hours, helpful, earlyAccess, free])
        
        reviewCounter += 1
        blankCoutdown = earlyAccessLimit
        
        if reviewCounter % reviewThreshold == 0:
            print(f"Reached {posted}. Saved {reviewCounter} reviews!")

#Saves to both the excel file and txt save file      
def saveReviews(reviews):
    
    colName = ['ReviewID', 'SteamID', 'Rating', 'Review', 'Date Posted', 'Hours Played', 'Voted Helpful', 'Early Access', 'Received for Free']
    
    if newFile:
        dataExcel = pd.DataFrame(columns=colName)
    else:
        dataExcel = pd.read_excel(filePath, engine='openpyxl')
        
    df = pd.DataFrame(reviews, columns=colName)
        
    dataExcel = pd.concat([dataExcel, df if not df.empty else None])
        
    dataExcel.to_excel(filePath, index=False)
    
    toSave = f"{startTime} {earlyAccessSave}"
    
    #Saves to last timestamp file
    with open(saveFile, 'w') as f:
        f.write(toSave)

#Loads Steam and begins to collect data!   
try:
    sleep(2)
    
    #Gets past the age check page for mature games
    if len(driver.find_elements_by_class_name('agegate_btn_ctn')) > 0:
        driver.execute_script("document.getElementById('ageYear').value = '2000';")
        driver.execute_script("ViewProductPage();")
    
    #First section initializes page with correct filters
    sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  
    running = True 
    
    #Clears potential filters
    sleep(2)
    driver.execute_script('ClearReviewLanguageFilter();')
    sleep(2)
    driver.execute_script('ClearOfftopicReviewActivityFilter();')
    
    sleep(2)
    #Sets context to 'recent'
    driver.execute_script("document.getElementById('review_context_recent').checked = true;")
    
    #Allows for date ranges to be created as a filter
    sleep(2)
    driver.execute_script("$J('#review_date_range_histogram').attr( 'checked', true );")
    driver.execute_script("UpdateActiveFilters();")
    
    #Sets inital time
    startTime = findInitialTimestamp()
    
    sleep(2)
    #Finds number of reviews from last used (0 if new)
    driver.execute_script(f'document.getElementById("review_start_date").setAttribute("value", "{startTime}");')
    driver.execute_script(f'document.getElementById("review_end_date").setAttribute("value", "{endTime}");')
    driver.execute_script('ShowFilteredReviews();')
    
    
    sleep(2)
    #Finds total number of reviews
    totalReviews = howManyReviews()
    
    while running:
        
        #Only when all reviews before and after the game released are recorded, 'running' will be false when the loop ends.
        if(startTime < earlyAccessSave):
            running = False
        
        #Truncates dates to allow for chrome memory managment
        if totalReviews > reviewThreshold:
            if hourly > 0:
                endTime = startTime + 3600
                hourly -=1
            else:
                endTime = startTime + 86400
            
            #Sets range of dates and activates filters
            driver.execute_script(f'document.getElementById("review_start_date").setAttribute("value", "{startTime + 1}");')
            driver.execute_script(f'document.getElementById("review_end_date").setAttribute("value", "{endTime}");')
            driver.execute_script('ShowFilteredReviews();')
            
            running = True
        
        #At this point, we can pull all reviews
        sleep(2)
    
        #For very full days, break into hourly chunks. Assume these chunks are less than the review threshold. 
        if howManyReviews() > reviewThreshold and hourly == 0:
            hourly = 24
            continue
        
        #Extract reviews! Quit when chrome is scrolling for progress to save
        while True:
            try:
                sleep(2)
                driver.find_element_by_xpath('//*[@id="LoadMoreReviewsrecent"]/a').click()
            except Exception:
                if len(driver.find_elements_by_class_name('no_more_reviews')) > 0:
                    aquireData()
                    break
        
        startTime = endTime
        
        #When this reaches present day
        if (startTime >= midnight or blankCoutdown == 0) and running:
            startTime = earlyAccessSave - 86400
            endTime = earlyAccessSave

            driver.execute_script(f'document.getElementById("review_start_date").setAttribute("value", "{1}");')
            driver.execute_script(f'document.getElementById("review_end_date").setAttribute("value", "{endTime}");')
            driver.execute_script('ShowFilteredReviews();')
            
            totalReviews = howManyReviews()
            blankCoutdown = earlyAccessLimit
            
        #Cycles through days sequentially starting from the day before the game officially released to whenever reviews end.
        #For non-Early access games this will never trigger
        elif startTime == earlyAccessSave and running:
            earlyAccessSave -= 86400
            startTime = earlyAccessSave - 86400
            blankCoutdown -= 1
            

#Quit while code is loading more reviews to save progress!
except Exception  as e:
    print(e)
    if startTime <= earlyAccessSave:
        startTime = midnight

#Saves reviews and sets up for future use 
finally:
    if(not running):
        print('All caught up! And... ')
        startTime = midnight
        earlyAccessSave = 1
    
    driver.quit()
    
    saveReviews(reviews)
    
    print("All Done!")