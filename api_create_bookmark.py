#================================================================================
# File:         api_create_bookmark.py
# Type:         python script
# Date:         23-August 2019
# Author:       Carlos Cuellar - 23/August/2019
# Ownership:    This script is owned and maintained by the user, not by Delphix
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
# Description:
#
#       Script to be used to pull storage details from objects from all Delphix Engine configured in DXToolkit
#
# Prerequisites:
#   Python 2/3 installed
#
#
# Usage
#   python api_create_bookmark.py <DELPHIX_ADMIN> <PASSWORD> <DELPHIX_ENGINE> <TEMPLATE_NAME> <CONTAINER_NAME> <BRANCH_NAME> <BOOKMARK_NAME> <POINT_IN_TIME>  <EXPIRATION_DATE> <BOOKMARK_OPERATION>
#
#
# Example
#   python api_create_bookmark.py admin delphix delphixengine test1 testc1 branch1 carlos_test_2 2019-08-22T20:15:00.000Z  2019-08-24T20:15:00.000Z CREATE
#================================================================================
#
import sys
import requests
import json


#DATE FORMAT IS "[yyyy]-[MM]-[dd]T[HH]:[mm]:[ss].[SSS]Z"
DMUSER=sys.argv[1]
DMPASS=sys.argv[2]
DX_ENGINE=sys.argv[3]
DX_TEMPLATE=sys.argv[4]
DX_CONTAINER=sys.argv[5]
DX_BRANCH=sys.argv[6]
DX_BOOKMARK=sys.argv[7]
DX_BM_TIME=sys.argv[8]
DX_BM_EXPIRATION=sys.argv[9]
DX_CREATE_DELETE=sys.argv[10]
BASEURL='http://' + DX_ENGINE + '/resources/json/delphix'

print (BASEURL)


#
# Request Headers ...
#
req_headers = {
   'Content-Type': 'application/json'
}

#
# Python session, also handles the cookies ...
#
session = requests.session()

#
# Create session ...
#
formdata = '{ "type": "APISession", "version": { "type": "APIVersion", "major": 1, "minor": 10, "micro": 0 } }'
r = session.post(BASEURL+'/session', data=formdata, headers=req_headers, allow_redirects=False)

#
# Login ...
#
formdata = '{ "type": "LoginRequest", "username": "' + DMUSER + '", "password": "' + DMPASS + '" }'
r = session.post(BASEURL+'/login', data=formdata, headers=req_headers, allow_redirects=False)

#
# Get Delphix Self Service Template details ...
#
template = session.get(BASEURL+'/selfservice/template', headers=req_headers, allow_redirects=False)

#
# JSON Parsing ...
#
templatef = json.loads(template.text)

#
# Look for Delphix Self Service Template reference
#
for dbobj in templatef['result']:
    if dbobj['name'] == DX_TEMPLATE:
       DX_TEMPLATE_REF = dbobj['reference']
       print ( DX_TEMPLATE + ':' + DX_TEMPLATE_REF)

#
# Get Delphix Self Service Container details ...
#
container = session.get(BASEURL+'/selfservice/container', headers=req_headers, allow_redirects=False)

#
# JSON Parsing ...
#
containerf = json.loads(container.text)

#
# Get Delphix Self Service Container reference ...
#
for dbobj in containerf['result']:
    if dbobj['name'] == DX_CONTAINER:
        if dbobj['template'] == DX_TEMPLATE_REF:
            DX_CONTAINER_REF = dbobj['reference']
            print ( DX_CONTAINER + ':' + DX_CONTAINER_REF)


#
# Get Delphix Self Service Branch details ...
#
branch = session.get(BASEURL+'/selfservice/branch', headers=req_headers, allow_redirects=False)

#
# JSON Parsing ...
#
branchf = json.loads(branch.text)

#
# Get Delphix Self Service Branch reference ...
#
for dbobj in branchf['result']:
    if dbobj['name'] == DX_BRANCH:
        if dbobj['dataLayout'] == DX_CONTAINER_REF:
            DX_BRANCH_REF = dbobj['reference']
            print ( DX_BRANCH + ':' + DX_BRANCH_REF)

#
# Create or Delete Bookmark accordingly ...
#
if DX_CREATE_DELETE == "CREATE":
    #
    # Create JSON format parameters for API call to create Delphix Self Service Bookmark
    #
    print ('Creating bookmark ' +  DX_BOOKMARK + ' on branch ' + DX_BRANCH + ' on container  ' +  DX_CONTAINER + ' from template ' + DX_TEMPLATE + '...')
    formdata = '{ "type": "JSBookmarkCreateParameters" , "bookmark": { "type": "JSBookmark", "name": "' + DX_BOOKMARK + '" ,  "branch": "' + DX_BRANCH_REF + '", "expiration": "' + DX_BM_EXPIRATION + '" }, "timelinePointParameters": { "type": "JSTimelinePointTimeInput", "time": "' + DX_BM_TIME + '", "branch": "' + DX_BRANCH_REF + '" } }'
    #
    # Execute API call to create Delphix Self Service Bookmark
    #
    createbookmark = session.post(BASEURL+'/selfservice/bookmark', data=formdata, headers=req_headers, allow_redirects=False)
elif DX_CREATE_DELETE == "DELETE":
    #
    #Get Delphix Self Service Bookmark details
    #
    bookmark = session.get(BASEURL+'/selfservice/bookmark', headers=req_headers, allow_redirects=False)

    #
    # JSON Parsing ...
    #
    bookmarkf = json.loads(bookmark.text)

    #
    #Get Delphix Self Service Bookmark reference
    #
    for dbobj in bookmarkf['result']:
        if dbobj['name'] == DX_BOOKMARK:
            DX_BOOKMARK_REF = dbobj['reference']
            print ( DX_BOOKMARK + ':' + DX_BOOKMARK_REF)
    #
    # Execute API call to delete Delphix Self Service Bookmark
    #
    print ('Delete bookmark ' +  DX_BOOKMARK + ' created previously on  branch ' + DX_BRANCH + ' on container  ' +  DX_CONTAINER + ' from template ' + DX_TEMPLATE + '...')
    createbookmark = session.post(BASEURL+'/selfservice/bookmark/' + DX_BOOKMARK_REF + '/delete', headers=req_headers, allow_redirects=False)
else:
    print ("Please specify CREATE or DELETE Bookmark only")

print ('------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
