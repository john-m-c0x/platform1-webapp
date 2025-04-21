import json
import boto3
import logging
import os
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS Resources
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'train_departures'))

def lambda_handler(event, context):
    try:
        logger.info("API Lambda execution started")
        
        # Retrieve train departure data from DynamoDB
        try:
            response = table.get_item(
                Key={
                    'id': 'platform1_departures'
                }
            )
            
            item = response.get('Item', {})
            
            if not item:
                logger.warning("No train departure data found in DynamoDB")
                return {
                    'statusCode': 404,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'GET, OPTIONS'
                    },
                    'body': json.dumps({
                        'departures': [],
                        'lastUpdated': None,
                        'updating': False,
                        'error': 'No departure data available'
                    })
                }
            
            # Format response to match your frontend expectations
            response_data = {
                'departures': item.get('departures', []),
                'lastUpdated': item.get('last_updated', None),
                'updating': False  # Always false since we're not tracking update status
            }
            
            logger.info(f"Retrieved {len(response_data['departures'])} departures, last updated at {response_data['lastUpdated']}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS'
                },
                'body': json.dumps(response_data)
            }
            
        except ClientError as e:
            logger.error(f"Error retrieving data from DynamoDB: {e}")
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Error retrieving train departure data'
                })
            }
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        } 