"""
This script downloads qualtrics survey files with spliter.
"""
__author__ = 'Hans Fricke'
__version__ = '0.1'
__date__ = '12-01-2018'

from splinter import Browser
from splinter import exceptions
from time import sleep
import pandas as pd

## Things to add:
# - firefox setting file path
firefox_file_path = r'/Users/hansfricke/Library/Application Support/Firefox/Profiles/9l8llqcs.default'
# - csv file with list of surveys
survey_list_file = '/Users/hansfricke/Dropbox/Surveys.csv'
# - column name for the column that holds survey names
column_name = 'Name'

# program will ask for qualtrics username and password

# decorator function to give pages enough time to load before finding element
def wait_until_loaded(func):
    def func_wrapper(br, *args):
        loaded = 0
        attempts = 0
        while loaded==0 | attempts < 5:
            attempts+=1
            try:
                func(br, *args)
            except (ValueError, exceptions.ElementDoesNotExist):    
                sleep(1)
            else:
                loaded = 1  
        return loaded
    return func_wrapper       

def click_tools(br):
    '''Clicks tools menu'''
    br.find_by_css('.Tools>.btn')[0].click()
 
@wait_until_loaded    
def search_dropdown(br, search_for):
    '''Searches tools dropdown menu, then clicks or mouse over depending on input'''
    menu_items = br.find_by_css('div.qmenu.dropdown-menu.positioned>ul>li')
    index = [item.text for item in menu_items].index(search_for)
    if search_for == 'Export Survey':
        menu_items[index].click()
    else:
        menu_items[index].mouse_over()

@wait_until_loaded 
def check_if_main_page(br):
    '''In combination with decorator, checks if main page has loaded'''
    br.find_by_css('.project-name')
    
def go_to_survey(br, survey):
    '''Click the corresponding survey link on main page'''
    br.find_by_text(survey)[0].click()  

def is_last_page(br):
    '''In search of survey link, checks if last page has been reached'''
    page_message = br.find_by_css('.pagination>.message').text.split()
    current_page, last_page = page_message[2], page_message[4]
    return current_page == last_page   

def go_to_next_page(br):
    '''Goes to next page if survey link not found'''
    br.find_by_css('.forward')[0].click()
    
def go_to_start(br):
    '''Goes back to main page after download'''
    br.find_by_css('.bread-crumb-nav-container>.xm-dots')[0].click()
 
 
# start program ---------------    
if __name__=="__main__":
    
    user = input("Qualtrics user name: ")
    password = input("Qualtrics password: ")

    # It is important to use the profile file for Firefox 
    # with the setting that the Qualtrics file type will always be downladed
    browser = Browser('firefox', profile=firefox_file_path)
    
    # Go to Qualtrics website
    browser.visit('https://www.qualtrics.com/login')

    # Enter username and password and log in
    browser.find_by_id('UserName').fill(user)
    browser.find_by_id('UserPassword').fill(password)
    browser.find_by_id('loginButton').click()    
    
    # Load the names of the surveys into a list 
    survey_list =  pd.read_csv(survey_list_file)
    surveys = list(survey_list[column_name])

    # For each survey, execute:
    for survey in surveys:
        found = 0
        while found==0:      
            #check if main page is loaded
            check_if_main_page(browser)  
            #check if survey on current page        
            try:
                go_to_survey(browser, survey)
            except exceptions.ElementDoesNotExist:
                # if not
                # check if last page
                # if last page, survey cannot be found
                if is_last_page(browser):
                    print('Survey:', survey, 'not found!')
                    found = 1
                    go_to_start(browser)
                    continue
                # otherwise, look on next page
                go_to_next_page(browser)
            else:
                # if survey on page, initiate download
                success = 0
                while success == 0: 
                    sleep(1)
                    # click on tools buttoon 
                    try:
                        click_tools(browser)
                    except exceptions.ElementDoesNotExist:
                        continue
                    else:
                        # hover mouse over Import/Export
                        search_dropdown(browser, 'Import/Export')
                        # click on 'Export Survey'
                        success = search_dropdown(browser, 'Export Survey')
                # set found to 1        
                found = 1
                # go back to the first page
                go_to_start(browser)
                