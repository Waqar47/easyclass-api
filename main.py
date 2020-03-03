import requests
import json
from bs4 import BeautifulSoup


proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
#r = requests.get("https://www.google.com/", proxies=proxies, verify=False)
user_agent = "waleed"


def post_info(json):
    updates = json['data']['updates']
    posts = []
    
    for post in updates:
        body = updates['body']
        time_stamp = updates['timestamp']
        
        posts.append({'body':body,'timestamp':time_stamp})
    
    return posts
        

def get_instructor_info(json):
    #magic
    id = list(json['data']['users'])[0]
    
    faculty_data = json['data']['users'][id]
    
    first_name = faculty_data['first_name']
    last_name = faculty_data['last_name']
    
    role = faculty_data['role']
    
    details = {'first_name':first_name,'last_name':last_name,'role':role}
    
    return details
    
    
    
def get_auth_cookie(cookies,c_type,auth):
    
    request_obj = requests.Session()
    response = request_obj.post('https://easyclass.com/site_auth/login',cookies=cookies,headers=c_type,data=auth)
    auth_cookie = response.cookies.get_dict()
    return auth_cookie
    
    
    
def get_wall_json(request_obj,links,cookie):
    
    json = ''
    for link in links:
        
        link = link['href']
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
        
def get_course_links_names(request_obj,cookies,c_type,auth):
    response = request_obj.post('https://easyclass.com/site_auth/login',cookies=cookies,headers=c_type,data=auth)
    
    soup = BeautifulSoup(response.text,'html.parser')
    
    if(response.status_code == 200):
        list_items  = soup.ul.find_all('li')
    else:
        print('[!] get_course_link_names() request failed')
        exit(1)
    
    links_names = []
    
    for i in range(0,len(list_items)):
        if not 'NoneType' in str(type(list_items[i].a)):
            links_names.append({'href':list_items[i].a['href'],'text':list_items[i].a.text})
    
    return links_names



def session_requests():
    email,password=get_easy_creds()
    
    c_type = {'Content-Type': 'application/x-www-form-urlencoded','User-Agent':user_agent}
    cookie_part1 = requests.get('https://easyclass.com/').cookies.get_dict()
    
    
    
    auth = 'email=%s&password=%s' % (email,password)
    
    home = requests.Session()
    
    links_names = get_course_links_names(home,cookie_part1,c_type,auth)
    cookie = get_auth_cookie(cookie_part1,c_type,auth)
    
    json_dict = get_wall_json(home,links_names,cookie_part1)
    
    faculty_info = get_instructor_info(json_dict)
    
    
    write_wall_html(faculty_info,json_dict,links_names)
                    
    
    
          
    



def write_wall_html(faculty_info,posts,links_names):
    soup = BeautifulSoup(open('template\my_wall.html'),'html.parser')
    body = soup.find('body')
    
    faculty = soup.new_tag('p',hidden='true',id='faculty_info')
    posts_tag = soup.new_tag('p',hidden='true',id='posts')
    links_tag = soup.new_tag('p',hidden='true',id='courses_info')
    script = soup.new_tag('script',src="js/script.js")
    
    faculty.string = json.dumps(faculty_info)
    posts_tag.string = json.dumps(posts)
    links_tag.string = json.dumps(links_names)
    
    body.append(faculty)
    body.append(posts_tag)
    body.append(links_tag)
    body.append(script)
    
    out = open('my_wall.html','w')
    out.write(str(soup))
    
    
    
    
    
    
    
    
        
    
    
    
    
    



if __name__ == '__main__':
    session_requests()