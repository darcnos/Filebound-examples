
import base64, requests, json, os, glob

fbheaders = {'content-type': 'application/json'}
siteurl = input('https://')
current_dir = os.path.dirname(os.path.realpath(__file__))



def login(siteurl):
    """Logs into the site and returns a GUID"""
    u = input('Username: ')
    p = input('Password: ')

    data = {
        'username': u,
        'password': p
    }

    login = 'https://{}/api/login'.format(siteurl)
    r = requests.post(login, data)
    return r.json()


def get_file_template():
    """Requests and returns a file template dictionary"""
    return json.loads(requests.get('https://{}/api/empty?template=file'.format(siteurl)).text)


def get_doc_template():
    """Requests and returns a document template dictionary"""
    return json.loads(requests.get('https://{}/api/empty?template=file'.format(siteurl)).text)


def query_file(keyfield):
    """Using the keyfield, find a file and return its listing of documents"""
    r = requests.get('https://{}/api/query/projectId_25/F1_{}/divider_/binaryData?guid={}'.format(siteurl, keyfield, guid))

    if r.status_code == 200:
        contents = r.json()
        
        if contents[0]['files']['totalCount'] == 0:
            print('No file found.')
        else:
            print('Found the file!')
            download_documents(current_dir + '/download_documents', contents, keyfield)


def download_documents(download_path, contents, keyfield):
    """Reads and saves out the documents from the response of a file query"""
    for document in contents[0]['files']['collection'][0]['documents']['collection']:        
        if not os.path.exists(download_path):
            os.makedirs(download_path)
            
        binaryData = base64.b64decode(document['binaryData'])
        documentId = document['documentId']
        extension = document['extension']

        output = download_path + '/' + str(documentId) + '.{}'.format(extension)
        print('Saving documents to {}'.format(output))
        
        with open(output, 'wb') as f:
            f.write(binaryData)
            f.close()

        
def upload_documents(directory_to_upload):
    """Takes a folder path, reads the path's contents, and uploads it to a file based
    on the file's keyfield"""

    #New file Post string, this example uses projectId 25
    post_file_string = 'https://{}/api/projects/25/files?guid={}'
    post_doc_string = 'https://{}/api/documents/{}?guid={}'


    #Find all files in a directory
    filelist = [filename for filename in glob.glob(directory_to_upload + '/\*.*')]
    print(filelist)

    for file in filelist:

        #Create a copy of the FileBound file and document templates
        file_temp = file_template.copy()
        doc_temp = doc_template.copy()

        #Read file name and extension
        base = os.path.basename(file)
        ext = os.path.splitext(base)[1][1:]

        #Populate the file template's Index Field 1 with a value
        file_temp['field'][1] = input('Enter a value to place into Field1: ')

        #Read the current file we are iterating over
        with open(file, 'rb') as current_file:
            binaryData = base64.b64encode(current_file.read()).decode('utf-8')
            payload = json.dumps(file_temp)

            #Put a new file in the project
            r = requests.put(post_file_string.format(siteurl, guid), payload, headers=fbheaders)
            print(r.text)

            #If the PUT is successful, a fileId will be returned
            #This string is either for a new fileId, or the fileId of an existing file based on merge rules
            if not r.status_code == 200:
                print('error POSTing to file')
            else:

                fileId = r.text

                #Fill the document template with binaryData, the mimetype, a divider (optional)
                #and set it to allow the data be saved to the site
                doc_temp['binaryData'] = binaryData
                doc_temp['extension'] = ext
                doc_temp['divider'] = 'my_divider'
                doc_temp['allowSaveBinaryData'] = True

                #Dump the contents to a JSON string so it can be POSTed
                doc_post_object = json.dumps(doc_temp)

                docpost_r = requests.put(post_doc_string.format(siteurl, fileId, guid), doc_post_object, headers=fbheaders)

                #If the POST is successful, the newly created documentId will be the response
                print(docpost_r.text)
    return True



if __name__ == '__main__':
    #Login and return a GUID
    guid = login(siteurl)

    #Query a file, see if it exists and download it if found
    response = query_file('test')
    response2 = query_file('some other value')

    #get a file and document template
    file_template = get_file_template()
    doc_template = get_doc_template()

    #Upload the files in current_directory's 'upload_documents' folder    
    upload_documents(current_dir + '/upload_documents/')

