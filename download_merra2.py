"""
Example how to download MERRA-2 data, based on the instructions here: 
https://disc.gsfc.nasa.gov/information/howto?keywords=API&title=How%20to%20Use%20the%20Web%20Services%20API%20for%20Subsetting%20MERRA-2%20Data (example 3)
Requires an Earthdata account that is linked with the GESDISC archive: https://disc.gsfc.nasa.gov/information/documents?title=Data%20Access
"""



# 1. import the required Python libraries

import sys
import json
import urllib3
import certifi
import requests
from time import sleep
from http.cookiejar import CookieJar
import urllib.request
from urllib.parse import urlencode
import getpass


# 2. initialize the urllib PoolManager, set URL for the API requests to the GES DISC subsetting service

# Create a urllib PoolManager instance to make requests.
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
# Set the URL for the GES DISC subset service endpoint
url = 'https://disc.gsfc.nasa.gov/service/subset/jsonwsp'




# 3. define method to submit a JSON-formatted Web Services Protocol (WSP) request to the GES DISC server

# This method POSTs formatted JSON WSP requests to the GES DISC endpoint URL
# It is created for convenience since this task will be repeated more than once
def get_http_data(request):
    hdrs = {'Content-Type': 'application/json',
            'Accept'      : 'application/json'}
    data = json.dumps(request)       
    r = http.request('POST', url, body=data, headers=hdrs)
    response = json.loads(r.data)   
    # Check for errors
    if response['type'] == 'jsonwsp/fault' :
        print('API Error: faulty %s request' % response['methodname'])
        sys.exit(1)
    return response

"""
NOT CURRENTLY WORKING:
# 3.5 You can use the API to do a Dataset Search in order to find out the exact name of the data product and its variables. 

#https://disc.gsfc.nasa.gov/information/howto?keywords=api&title=How%20to%20Use%20the%20Web%20Services%20API%20for%20Dataset%20Searching
# Prompt for search string keywords
# This will keep looping and prompting until search returns an error-free response
done = False
while done is False :
  myString=''
  while len(myString) < 1 : 
    myString = input("Enter search keywords: ")

  # Set up the JSON WSP request for API method: search
  search_request = {
    'methodname': 'search',
    'type': 'jsonwsp/request',
    'version': '1.0',
    'args': {'search': myString}
  }

  # Submit the search request to the GES DISC server
  hdrs = {'Content-Type': 'application/json',
          'Accept': 'application/json'}
  data = json.dumps(search_request)
  r = http.request('POST', url, body=data, headers=hdrs)
  response = json.loads(r.data)

  # Check for errors
  if response['type']=='jsonwsp/fault' :
    print('ERROR! Faulty request. Please try again.')
  else : 
    done = True
print('OK')

# Indicate the number of items in the search results
total = response['result']['totalResults']
if total == 0 :
    print('Zero items found')
elif total == 1 : 
    print('1 item found')
else :          
    print('%d items found' % total)
"""

# 4. Define the dataset/product and parameters

# Here, we use the MERRA-2 Monthly 2-Dimensional Time-Averaged Variables 
# M2TMNXAER: contains a time-averaged 2-dimensional monthly mean data collection
# selected variable in this example is: so4 extinction [550 nm] (SUEXTTAU). 
#tavg1_2d_flx_Nx (M2T1NXFLX): Surface Flux Diagnostics
# tavg1_2d_lnd_Nx (M2T1NXLND): Land Surface Diagnostics
#PRECTOT / or for the latter PRECTOTLAND

# Define the parameters for the third subset example
#product = 'M2T1NXFLX'
#varNames =['PRECTOT']
product = 'M2T1NXFLX_V5.12.4' 
varNames =['PRECTOT']
minlon = 70
maxlon = 90
minlat = 24
maxlat = 39
begTime = '1980-01'
endTime = '1980-02'
# possible to add regridding:
# interp = 'remapbil'
# destGrid = 'fv4x5'


# 5. Construct JSON WSP request for API method: subset

subset_request = {
    'methodname': 'subset',
    'type': 'jsonwsp/request',
    'version': '1.0',
    'args': {
        'role'  : 'subset',
        'start' : begTime,
        'end'   : endTime,
        'box'   : [minlon, minlat, maxlon, maxlat],
        'crop'  : True, 
        'data': [{'datasetId': product,
                  'variable' : varNames[0]
                 }]
    }
}
# to add interpolation, add the following keywords to the request: 
#        'mapping': interp,
#         'grid'  : destGrid,
# to add several datasets, add this to the request: 
#    , {'datasetId': product,
#              'variable' : varNames[0]
#             }


# 6. Submit the subset request to the GES DISC Server

response = get_http_data(subset_request)
# Report the JobID and initial status
myJobId = response['result']['jobId']
print('Job ID: '+myJobId)
print('Job status: '+response['result']['Status'])


# 7. Construct JSON WSP request for API method: GetStatus
status_request = {
    'methodname': 'GetStatus',
    'version': '1.0',
    'type': 'jsonwsp/request',
    'args': {'jobId': myJobId}
}

# Check on the job status after a brief nap
while response['result']['Status'] in ['Accepted', 'Running']:
    sleep(5)
    response = get_http_data(status_request)
    status  = response['result']['Status']
    percent = response['result']['PercentCompleted']
    print ('Job status: %s (%d%c complete)' % (status,percent,'%'))
if response['result']['Status'] == 'Succeeded' :
    print ('Job Finished:  %s' % response['result']['message'])
else : 
    print('Job Failed: %s' % response['fault']['code'])
    sys.exit(1)
    
    
# STEP 8: Construct JSON WSP request for API method: GetResult
batchsize = 20
results_request = {
    'methodname': 'GetResult',
    'version': '1.0',
    'type': 'jsonwsp/request',
    'args': {
        'jobId': myJobId,
        'count': batchsize,
        'startIndex': 0
    }
}

# Retrieve the results in JSON in multiple batches 
# Initialize variables, then submit the first GetResults request
# Add the results from this batch to the list and increment the count
results = []
count = 0 
response = get_http_data(results_request) 
count = count + response['result']['itemsPerPage']
results.extend(response['result']['items']) 

# Increment the startIndex and keep asking for more results until we have them all
total = response['result']['totalResults']
while count < total :
    results_request['args']['startIndex'] += batchsize 
    response = get_http_data(results_request) 
    count = count + response['result']['itemsPerPage']
    results.extend(response['result']['items'])
       
# Check on the bookkeeping
print('Retrieved %d out of %d expected items' % (len(results), total))



# 9. Sort the results into documents and URLs

docs = []
urls = []
for item in results :
    try:
        if item['start'] and item['end'] : urls.append(item) 
    except:
        docs.append(item)
# Print out the documentation links, but do not download them
# print('\nDocumentation:')
# for item in docs : print(item['label']+': '+item['link'])




# 10. Download with Requests Library:
# In STEP 10, for the request.get() module to work properly, you must have a HOME/.netrc file that contains the following text (configured with your own Earthdata userid and password): machine urs.earthdata.nasa.gov login [userid] password [password]. In the alternate STEP 10, you can provide your userid and password on-the-fly when running the code.

# Use the requests library to submit the HTTP_Services URLs and write out the results.
print('\nHTTP_services output:')
for item in urls :
    URL = item['link'] 
    result = requests.get(URL)
    try:
        result.raise_for_status()
        outfn = item['label']
        f = open(outfn,'wb')
        f.write(result.content)
        f.close()
        print(outfn, "is downloaded")
    except:
        print('Error! Status code is %d for this URL:\n%s' % (result.status.code,URL))
        print('Help for downloading data is at https://disc.gsfc.nasa.gov/data-access')
        
print('Downloading is done and find the downloaded files in your current working directory')


if 0:
    # ATLERNATIVE STEP 10 
    # Create a password manager to deal with the 401 response that is returned from
    # Earthdata Login
    
    # Create a password manager to deal with the 401 response that is returned from
    # Earthdata Login
    
    username = input("Provide your EarthData userid: ")
    password = getpass.getpass("Provide your EarthData password: ")
    
    password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, "https://urs.earthdata.nasa.gov", username, password)
    
    # Create a cookie jar for storing cookies. This is used to store and return the session cookie #given to use by the data server
    cookie_jar = CookieJar()
       
    # Install all the handlers.
    opener = urllib.request.build_opener (urllib.request.HTTPBasicAuthHandler (password_manager),urllib.request.HTTPCookieProcessor (cookie_jar))
    urllib.request.install_opener(opener)
     
    # Open a request for the data, and download files
    print('\nHTTP_services output:')
    for item in urls:
        URL = item['link'] 
        DataRequest = urllib.request.Request(URL)
        DataResponse = urllib.request.urlopen(DataRequest)
    
    # Print out the result
        DataBody = DataResponse.read()
    
    # Save file to working directory
        try:
            file_name = item['label']
            file_ = open(file_name, 'wb')
            file_.write(DataBody)
            file_.close()
            print (file_name, "is downloaded")
        except requests.exceptions.HTTPError as e:
             print(e)
                
    print('Downloading is done and find the downloaded files in your current working directory')




