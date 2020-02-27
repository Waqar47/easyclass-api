import requests
from bs4 import BeautifulSoup

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
#r = requests.get("https://www.google.com/", proxies=proxies, verify=False)
user_agent = "waleed"



def get_auth_cookie(cookies,c_type,auth):
    
    request_obj = requests.Session()
    response = request_obj.post('https://easyclass.com/site_auth/login',cookies=cookies,headers=c_type,data=auth)
    auth_cookie = response.cookies.get_dict()
    return auth_cookie
    
    
    
def get_wall_json(request_obj,links,cookie):
    
    json = ''
    for link in links:
        course_id = link.split('/')[2]
        url = 'https://easyclass.com/sectionupdates/%s/json/list' % course_id
        response = request_obj.post(url,cookies=cookie,headers = {'User-Agent':user_agent,'Referer':'https://easyclass.com/sections/'+course_id+'/updates','Accept': 'application/json, text/javascript, */*; q=0.01'})
        
        if(response.status_code == 200):
            json = response.json() 
        else:
            print('[!] get_wall_json() request failed')
            exit(1)

    return json

def get_easy_creds():
    with open('creds.txt') as file:
        txt = file.readline()
        email = txt.split(',')[0]
        password = txt.split(',')[1]
        
        return (email,password)
        
def get_course_links(request_obj,cookies,c_type,auth):
    response = request_obj.post('https://easyclass.com/site_auth/login',cookies=cookies,headers=c_type,data=auth)
    
    soup = BeautifulSoup(response.text,'html.parser')
    
    if(response.status_code == 200):
        list_items  = soup.ul.find_all('li')
    else:
        print('[!] get_course_link() request failed')
        exit(1)
    
    links = list_items[1].a['href']
    
    if type(links) == type(list):
        return links
        
    return [links]



def session_requests():
    email,password=get_easy_creds()
    
    c_type = {'Content-Type': 'application/x-www-form-urlencoded','User-Agent':user_agent}
    cookie_part1 = requests.get('https://easyclass.com/').cookies.get_dict()
    
    
    
    auth = 'email=%s&password=%s' % (email,password)
    
    home = requests.Session()
    
    
    
    #home.post('https://easyclass.com/site_auth/login',cookies=cookie_part1,headers=c_type,data=auth)
    #print(links)
    links = get_course_links(home,cookie_part1,c_type,auth)
    cookie = get_auth_cookie(cookie_part1,c_type,auth)
    
    print(get_wall_json(home,links,cookie_part1))
    
    
    
session_requests()    


def write_wall_html(data):
    pass