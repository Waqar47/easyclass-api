import requests

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

#r = requests.get("https://www.google.com/", proxies=proxies, verify=False)


def get_cookie(email,password):
    
    
    c_type = {'Content-Type': 'application/x-www-form-urlencoded'}
    cookie_part1 = requests.get('https://easyclass.com/').cookies.get_dict()
    
    
    auth = 'email=%s&password=%s' % (email,password)
    
    
    home = requests.post('https://easyclass.com/site_auth/login',cookies=cookie_part1,headers=c_type,data=auth,proxies=proxies,verify=False)
                         
    final_cookie = home.cookies.get_dict()
    
    return final_cookie

cookie = get_cookie('','')
print(cookie)

def get_wall_json(cookie):
    pass

def write_wall_html(data):
    pass