import requests
import json
import logging
from bs4 import BeautifulSoup
import threading
import queue as Queue

#proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
#r = requests.get("https://www.google.com/", proxies=proxies, verify=False)
user_agent = "Chrome"
domain = "easyclass.com"

#config logging
logging.basicConfig(level=logging.INFO)

def post_info(json):
    updates = json['data']['updates']
    posts = []
    
    for post in updates:
        body = updates['body']
        time_stamp = updates['timestamp']
        
        posts.append({'body':body,'timestamp':time_stamp})
    
    return posts
        

def get_instructor_info(json,my_queue):
    #magic
    id = list(json['data']['users'])[0]
    
    faculty_data = json['data']['users'][id]
    
    first_name = faculty_data['first_name']
    last_name = faculty_data['last_name']
    
    role = faculty_data['role']
    
    details = {'first_name':first_name,'last_name':last_name,'role':role}
    
    my_queue.put(details)
    
    
    
def get_auth_cookie(cookies,c_type,auth):
    
    request_obj = requests.Session()
    response = request_obj.post('https://' + domain + '/site_auth/login',cookies=cookies,headers=c_type,data=auth)
    auth_cookie = response.cookies.get_dict()
    return auth_cookie
    
    
    
def get_wall_json(request_obj,links,cookie,my_queue):
    
    json = ''
    for link in links:
        
        link = link['href']
        course_id = link.split('/')[2]
        url = 'https://' + domain + '/sectionupdates/%s/json/list' % course_id
        response = request_obj.post(url,cookies=cookie,headers = {'User-Agent':user_agent,'Referer':'https://' + domain + '/sections/'+course_id+'/updates','Accept': 'application/json, text/javascript, */*; q=0.01'})
        
        if(response.status_code == 200):
            json = response.json() 
        else:
            print('[!] get_wall_json() request failed')
            exit(1)

    my_queue.put(json)

def get_easy_creds():

    with open('creds.txt') as file:
        txt = file.readline()
        email = txt.split(',')[0]
        password = txt.split(',')[1]
        
        return (email,password)
        
def get_course_links_names(request_obj,cookies,c_type,auth,my_queue):
    response = request_obj.post('https://' + domain + '/site_auth/login',cookies=cookies,headers=c_type,data=auth)
    
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
    
    my_queue.put(links_names)



def session_requests():
    thread_ret_data = Queue.Queue()

    logging.info('Initiating session requests')
    logging.info('Reading... easyclass.com credentials')
    email,password=get_easy_creds()
    
    c_type = {'Content-Type': 'application/x-www-form-urlencoded','User-Agent':user_agent}
    cookie_part1 = requests.get('https://' + domain + '/').cookies.get_dict()
    
    
    
    auth = 'email=%s&password=%s' % (email,password)
    
    home = requests.Session()
    logging.info('Fetching... courses links and names')
    #get course links therad --start--
    links_names = threading.Thread(get_course_links_names(home,cookie_part1,c_type,auth,thread_ret_data))
    links_names.start()
    links_names.join()
    links_names = thread_ret_data.get()
    
    logging.info('Creating... authentication cookie')
    cookie = get_auth_cookie(cookie_part1,c_type,auth)
    
    logging.info('Fetching... student wall json blob')
    
    #get json data (thread) --start--
    json_dict = threading.Thread(target=get_wall_json(home,links_names,cookie_part1,thread_ret_data))
    json_dict.start()
    json_dict.join()

    json_dict = thread_ret_data.get()
    #thread --end--

    logging.info('Reading... instructor info')
    #faculty info thread --start--
    faculty_info = threading.Thread(get_instructor_info(json_dict,thread_ret_data))
    faculty_info.start()
    faculty_info.join()
    faculty_info = thread_ret_data.get()
    #thread --end--

    logging.info('Writing... templates/index.html')
    #write wall html thread --start--
    write_to_wall = threading.Thread(write_wall_html(faculty_info,json_dict,links_names))
    write_to_wall.start()
    write_to_wall.join()
    #write wall html thread --end--

                    
    
    
          
    



def write_wall_html(faculty_info,posts,links_names):
    soup = BeautifulSoup(open('templates/my_wall.html'),'html.parser')
    body = soup.find('body')
    
    faculty = soup.new_tag('p',hidden='true',id='faculty_info')
    posts_tag = soup.new_tag('p',hidden='true',id='posts')
    links_tag = soup.new_tag('p',hidden='true',id='courses_info')
    script = soup.new_tag('script',src="{{ url_for('static', filename='js/script.js') }}")
    
    faculty.string = json.dumps(faculty_info)
    posts_tag.string = json.dumps(posts)
    links_tag.string = json.dumps(links_names)
    
    body.append(faculty)
    body.append(posts_tag)
    body.append(links_tag)
    body.append(script)
    
    out = open('templates/index.html','w')
    out.write(str(soup))
    
    
    
