import requests
import json
import sys
import datetime

session = requests.Session()

if len(sys.argv) != 4:
    sys.exit("Not enough args supplied")
else:
    hostname = sys.argv[1] 
    username = sys.argv[2]
    password = sys.argv[3]

    base_url = f"http://{hostname}/htdocs"

    data = {
        'username': username,
        'password': password,
    }

    #login
    response_login = session.post(f"{base_url}/login/login.lua", data=data, verify=False)

    params = {
        'protocol': '6',
    }

    data = {
        'file_type_sel[]': 'active_code',
        'http_token' : datetime.datetime.now().timestamp() * 1000,
    }

    #generate backup file
    response = session.post(f"{base_url}/lua/ajax/file_upload_ajax.lua", params=params, data=data, verify=False)

    response_json = json.loads(response.content)

    if response_json.get('successful') == False:
        session.get(f"{base_url}/pages/main/logout.lsp", verify=False)
        sys.exit("Error with getting config")

    url = response_json['queryParams']

    #download backup file
    file_response = session.get(f"{base_url}/pages/base/file_http_download.lsp{url}", verify=False)

    #write backup file
    with open(f"{hostname}-{datetime.datetime.now().strftime('%I_%p_%d_%m_%Y')}.stk", 'wb') as file:
        file.write(file_response.content)

    #Removes file ready for download from switch, if NOT run will cause all next backups to fail
    response = session.get(f"{base_url}/pages/base/file_http_download.lsp{url}&remove=true", verify=False)

    session.get(f"{base_url}/pages/main/logout.lsp", verify=False)

    print("Successfully backed up")