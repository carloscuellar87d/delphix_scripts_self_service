#================================================================================
# File:         api_op_container.py
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
#   python api_create_branches.py <DELPHIX_ADMIN> <PASSWORD> <DELPHIX_ENGINE> <TEMPLATE_NAME> <CONTAINER_NAME> <CONTAINER_OPERATION> <BOOKMARK_NAME(for restore only)>
#
#
# Example
#
#   python api_op_container.py admin delphix delphixengine test1 testc1 RESTORE newbmk
#   python api_op_container.py admin delphix delphixengine test1 testc1 REFRESH
#   python api_op_container.py admin delphix delphixengine test1 testc1 RESET
#
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
DX_ACTION=sys.argv[6]

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
       #print ( DX_TEMPLATE + ':' + DX_TEMPLATE_REF)

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
            #print ( DX_CONTAINER + ':' + DX_CONTAINER_REF)


#
#Get Delphix Self Service Branch and Active Branch details
#
activebranch = session.get(BASEURL+'/selfservice/container', headers=req_headers, allow_redirects=False)
branch = session.get(BASEURL+'/selfservice/branch', headers=req_headers, allow_redirects=False)
#
# JSON Parsing ...
#
activebranchf = json.loads(activebranch.text)
branchf = json.loads(branch.text)
#
#Get Delphix Self Service Branch to delete and Active Branch reference
#
for dbobj in activebranchf['result']:
    if dbobj['name'] == DX_CONTAINER:
        if dbobj['template'] == DX_TEMPLATE_REF:
            DX_ACTIVE_BRANCH_REF = dbobj['activeBranch']
            #print ( DX_CONTAINER + ':' + DX_ACTIVE_BRANCH_REF)

for dbobj in branchf['result']:
    if dbobj['reference'] == DX_ACTIVE_BRANCH_REF:
        DX_BRANCH = dbobj['name']
        #print ( DX_BRANCH + ':' + DX_ACTIVE_BRANCH_REF)


#
# Create or Delete Bookmark accordingly ...
#
if DX_ACTION == "REFRESH":
    #
    # Create JSON format parameters for API call to create Delphix Self Service Bookmark
    #
    print ('Refresh container  ' +  DX_CONTAINER + ' from template ' + DX_TEMPLATE + ' with latest data from its parent (dSource or vDB)...')
    print ('Active branch is: ' + DX_BRANCH)
    formdata = '{ "type": "JSDataContainerRefreshParameters" , "forceOption": false }'
    #
    # Execute API call to create Delphix Self Service Bookmark
    #
    refreshcontainer = session.post(BASEURL+'/selfservice/container/' + DX_CONTAINER_REF + '/refresh', data=formdata, headers=req_headers, allow_redirects=False)
elif DX_ACTION == "RESET":
    #
    # Create JSON format parameters for API call to create Delphix Self Service Bookmark
    #
    print ('Reset container  ' +  DX_CONTAINER + ' from template ' + DX_TEMPLATE + ' to state on last Refresh/Restore operation...')
    print ('Active branch is: ' + DX_BRANCH)
    formdata = '{ "type": "JSDataContainerResetParameters" , "forceOption": false }'
    #
    # Execute API call to create Delphix Self Service Bookmark
    #
    resetcontainer = session.post(BASEURL+'/selfservice/container/' + DX_CONTAINER_REF + '/reset', data=formdata, headers=req_headers, allow_redirects=False)
elif DX_ACTION == "RESTORE":
    DX_BOOKMARK=sys.argv[7]
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
    print ('Restore container  ' +  DX_CONTAINER + ' from template ' + DX_TEMPLATE + ' to Bookmark ' + DX_BOOKMARK + ' ...')
    formdata = '{ "type": "JSDataContainerRestoreParameters" , "timelinePointParameters": { "type": "JSTimelinePointBookmarkInput", "bookmark": "' + DX_BOOKMARK_REF + '" }, "forceOption": false }'
    #
    # Execute API call to create Delphix Self Service Bookmark
    #
    restorecontainer = session.post(BASEURL+'/selfservice/container/' + DX_CONTAINER_REF + '/restore', data=formdata, headers=req_headers, allow_redirects=False)
else:
    print ("Please specify REFRESH or RESET only")

print ('------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
