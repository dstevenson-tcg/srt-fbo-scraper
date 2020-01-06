import json
import logging
import os
import sys
from random import randint
from datetime import datetime,timedelta,date



import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

def requests_retry_session(retries=3, 
                           backoff_factor=.3, 
                           status_forcelist=(500, 502, 503, 504), 
                           session=None):
    '''
    Use to create an http(s) requests session that will retry a request.
    '''
    session = session or requests.Session()
    retry = Retry(total = retries, 
                  read = retries, 
                  connect = retries, 
                  backoff_factor = backoff_factor, 
                  status_forcelist = status_forcelist)
    adapter = HTTPAdapter(max_retries = retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session

def get_org_request_details():
    # see https://open.gsa.gov/api/fh-fouo-api/
    BETA_SAM_API_KEY_PUB = os.getenv('BETA_SAM_API_KEY_PUB')
    if not BETA_SAM_API_KEY_PUB:
        logger.critical("Couldn't find BETA_SAM_API_KEY_PUB in environment variables")
        sys.exit(1)
    uri = 'https://api.sam.gov/prod/federalorganizations/v1/orgs'
    params = {'api_key': BETA_SAM_API_KEY_PUB}
    
    return uri, params

def get_doc_request_details(opp_id):
    # see https://open.gsa.gov/api/opportunities-api/#
    # download-all-attachments-as-zip-for-an-opportunity
    #system api
    #ALPHA_SAM_DOC_KEY = os.getenv('ALPHA_SAM_DOC_KEY')
    #SAM_AUTHORIZER = os.getenv('SAM_AUTHORIZER')
    #if ALPHA_SAM_API_KEY and SAM_AUTHORIZER:
        #uri = f'https://api-alpha.sam.gov/prodlike/opportunity/v3/api/{opp_id}/resources/download/zip'
        #params.update({'api_key': ALPHA_SAM_API_KEY})
    #elif BETA_SAM_API_KEY and SAM_AUTHORIZER:
        #uri = f'https://api.sam.gov/prod/opportunity/v1/api/{opp_id}/resources/download/zip'
        #params.update({'api_key': BETA_SAM_API_KEY})
    #else:
        #logger.critical("Unable to determine SAM API endpoint. Check env vars: {os.environ}")
        #sys.exit(1)
    #headers = {'Authorization': SAM_AUTHORIZER}
    #if ALPHA_SAM_DOC_KEY:
    #    uri = f'https://alpha.sam.gov/api/prodlike/opps/v3/opportunities/{opp_id}/resources/download/zip?api_key={ALPHA_SAM_DOC_KEY}'
    #elif BETA_SAM_DOC_KEY:
    #    uri = f'https://api.sam.gov/prod/opps/v3/opportunities/{opp_id}/resources/download/zip?api_key={BETA_SAM_DOC_KEY}&token=5d467c10-6671-4a8c-b288-ef9dab966588'
    #else:
    #    logger.critical("Unable to determine SAM API endpoint. Check env vars: {os.environ}")
    #    sys.exit(1)
    #open api key
    uri = f'https://beta.sam.gov/api/prod/opps/v3/opportunities/{opp_id}/resources/download/zip?api_key=undefined&token=56b883ff-c79f-4394-be1a-cd18cfae9a95'
    #system api
    #uri = f'https://api.sam.gov/prod/opps/v3/opportunities/{opp_id}/resources/download/zip?api_key={BETA_SAM_DOC_KEY}'

    return uri

def get_opp_request_details():
    # see https://open.gsa.gov/api/opportunities-api/#get-list-of-opportunities
    BETA_SAM_API_KEY = os.getenv('BETA_SAM_API_KEY_PUB')
    SAM_AUTHORIZER = os.getenv("SAM_AUTHORIZER")

    def random_N_digits(n):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return randint(range_start, range_end)

    random_int = str(random_N_digits(13))

    #params = {'noticeType': 'p,k,o',
    #          'size': '100',
    #          'sortBy': '-modifiedOn',
    #          'latest': True,
    #          'random': random_int,
    #          'api_key':BETA_SAM_API_KEY,
    #          'index':'opp',
    #          'publish_date.to':'2019-12-13-05:00',
    #          'publish_date.from':'2019-12-13-05:00'}

    today = datetime.today().strftime('%m/%d/%Y')
    yesterday = (date.today() - timedelta(days=1)).strftime('%m/%d/%Y')


    params = {'ptype': 'k',
        'api_key':BETA_SAM_API_KEY,
        'postedFrom':str(yesterday),
        'postedTo':str(today),
        'limit':100}

    #if ALPHA_SAM_API_KEY and SAM_AUTHORIZER:
    #    uri = 'https://api-alpha.sam.gov/prodlike/opportunity/v1/api/search'
    #    params.update({'api_key': ALPHA_SAM_API_KEY})
    #elif BETA_SAM_API_KEY and SAM_AUTHORIZER:
    #    uri = 'https://api.sam.gov/prod/opportunity/v1/api/search'
    #    params.update({'api_key': BETA_SAM_API_KEY})
    #else:
    #    logger.critical("Unable to determine SAM API endpoint. Check env vars: {os.environ}")
    #    sys.exit(1)

    #open api
    #uri ="https://beta.sam.gov/api/prod/sgs/v1/search"
    #uri = 'https://api.sam.gov/prod/opportunity/v1/api/search'
    #public api
    
    uri = 'https://api.sam.gov/prod/opportunities/v1/search'
    



    headers = {'Authorization': SAM_AUTHORIZER}
    
    return uri, params, headers

def get_opps(uri, params, headers):

    #def random_N_digits(n):
    #    range_start = 10**(n-1)
    #    range_end = (10**n)-1
    #    return randint(range_start, range_end)
    #random_int = random_N_digits(13)
    #params2 = {'noticeType': 'p,k,o',
    #        'size': '100',
    #        'sortBy': '-modifiedOn',
    #        'latest': False,
    #        'random':str(random_N_digits(13)),
    #        'index':'opp',
    #        'api_key' : '',
    #        'random' : str(random_int),
    #        }
    ##headers2 = {'Authorization': SAM_AUTHORIZER}
    #opp_api2 = 'https://beta.sam.gov/api/prod/sgs/v1/search'

    try:
        r = requests.get(uri, params = params, timeout = 100, headers = headers)
    except Exception as e:
        print('except')
        logger.critical(f"Exception {e} getting opps from {uri}", exc_info=True)
        sys.exit(1)
    data = r.json()
    opps = data['opportunitiesData']
    total_pages = data['totalRecords']/100 + 1

    #with open('data.json','r') as myfile:
    #    data = myfile.read()
    #
    #data = json.loads(data)

    #try:
    #    #prior coding
    #    #opps = data['_embedded']['results']
    #    #total_pages = data['page']['totalPages']
    #
    #    #BS codes
    #    total_pages = data['totalRecords']
    #    opps = data['opportunitesData']
    #    print(opps)
    #except KeyError as e:
    #    error_message = data.get('errormessage','')
    #    data_str = json.dumps(data)
    #    #if not "request's IP does not match any pattern" in error_message:
    #    #    logger.error(f"Confirm API stability:\n{data_str}")
    #    #else:
    #    #    logger.error(f"{e}: making request to {uri}:\n{data_str}")
    #    return None, None
    return opps, total_pages

