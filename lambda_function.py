import json
import logging
import os

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# The log level
log_level = os.environ['log_level'].upper()

hook_url   = os.environ['hook_url']
channel    = os.environ['channel']
# high: #8b0000 medium: #ff8c00 low: #fafad2
color      = os.environ['color']

logger = logging.getLogger()
logger.setLevel(log_level)

def push_slack(slack_request):
    hook_url = slack_request['hook_url']
    slack_message =slack_request['msg']
    
    req = Request(hook_url, json.dumps(slack_message).encode('utf-8'))
    
    try:
      response = urlopen(req)
      response.read()
      logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
      logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
      logger.error("Server connection failed: %s", e.reason)

def check_event(event):
    
    slack_request = {}
    account = event['account']
    region  = event['region']
    detail  = event['detail']
    
    event_service       = detail['service']
    event_type          = detail['eventTypeCode']
    event_category      = detail['eventTypeCategory']
    event_start_time    = detail['startTime']
        
    slack_request = {
            "hook_url" : hook_url,
            "msg" : {
              "channel" : channel,
              "username" : "AWS health alert: %s" %(account),
              "text" : "*Event type: %s*" % (event_type),
              "attachments": [
                  {
                    "color": color,
                    "fields": [
                        {
                            "title": "Category",
                            "value": event_category,
                            "short": True
                        },
                        {
                            "title": "Region",
                            "value": region,
                            "short": True
                        },
                        {
                            "title": "Affect service",
                            "value": event_service,
                            "short": True
                        },
                        {
                            "title": "Start time",
                            "value": event_start_time
                        }
                    ],
                  }
                ]
            }
        }
    return slack_request

def lambda_handler(event, context):
    logger.info("Event: " + str(event))
    slack_request = check_event(event)
    if slack_request == None:
        pass
    else:
        push_slack(slack_request)
        
    return {
        'statusCode': 200,
        'body': json.dumps('Alert from AWS health!')
    }
