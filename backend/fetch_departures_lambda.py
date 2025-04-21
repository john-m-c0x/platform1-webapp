import json
import boto3
import requests
import hmac
from hashlib import sha1
import os
from datetime import datetime
import pytz
import logging
from botocore.exceptions import ClientError

"""
Lambda function to fetch transit departures from a public transit API.
Stores the results in DynamoDB for quick access by the frontend.

Required environment variables:
- API_DEV_ID: Your transit API developer ID
- API_KEY: Your transit API key
- STOP_ID: The station/stop ID to fetch departures for
- DYNAMODB_TABLE: DynamoDB table name for storing departures
- TIMEZONE: Timezone for departure times (default: 'UTC')
"""

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# API Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "https://timetableapi.ptv.vic.gov.au")
DEV_ID = os.environ.get("API_DEV_ID", "")
API_KEY = os.environ.get("API_KEY", "")
STOP_ID = int(os.environ.get("STOP_ID", "0"))
LOCAL_TZ = pytz.timezone(os.environ.get('TIMEZONE', 'UTC'))

# AWS Resources
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', ''))

def get_local_time():
    # Get current time in configured timezone
    return datetime.now(LOCAL_TZ)

def generate_signature(request_path):
    # Generate HMAC signature for API request
    request_path = request_path + ('&' if ('?' in request_path) else '?')
    raw = f"{request_path}devid={DEV_ID}"
    hashed = hmac.new(API_KEY.encode('utf-8'), raw.encode('utf-8'), sha1)
    return hashed.hexdigest().upper()

def get_api_url(endpoint):
    # Generate signed API URL
    request_path = endpoint
    request_path = request_path + ('&' if ('?' in request_path) else '?')
    raw = f"{request_path}devid={DEV_ID}"
    signature = generate_signature(endpoint)
    return f"{API_BASE_URL}{raw}&signature={signature}"

def parse_departure_data(departure, routes, directions, runs, disruptions=None):
    """
    Parse raw departure data into a standardized format.
    
    Args:
        departure (dict): Raw departure data
        routes (dict): Route information
        directions (dict): Direction information
        runs (dict): Run information
        disruptions (dict, optional): Disruption information
        
    Returns:
        dict: Formatted departure information
    """
    route_id = str(departure.get('route_id', ''))
    direction_id = str(departure.get('direction_id', ''))
    run_id = str(departure.get('run_id', ''))
    
    route_info = routes.get(route_id, {}) if routes else {}
    direction_info = directions.get(direction_id, {}) if directions else {}
    run_info = runs.get(run_id, {}) if runs else {}
    
    # Get destination information
    destination = run_info.get('destination_name') or direction_info.get('direction_name') or 'Unknown'
    
    # Handle scheduled time
    scheduled_time_utc = departure.get('scheduled_departure_utc')
    if not scheduled_time_utc:
        logger.error(f"Missing scheduled_departure_utc in departure data: {departure}")
        scheduled_time = get_local_time()
    else:
        scheduled_time = datetime.fromisoformat(scheduled_time_utc.replace('Z', '+00:00')).astimezone(LOCAL_TZ)
    
    estimated_time_utc = departure.get('estimated_departure_utc')
    
    # Get vehicle information
    vehicle_info = run_info.get('vehicle_descriptor', {}).get('description') if run_info else None
    
    # Get disruption information
    disruption_info = []
    if disruptions and departure.get('disruption_ids'):
        for disruption_id in departure.get('disruption_ids', []):
            disruption_id_str = str(disruption_id)
            if disruption_id_str in disruptions:
                disruption_info.append({
                    'title': disruptions[disruption_id_str].get('title', ''),
                    'description': disruptions[disruption_id_str].get('description', '')
                })
    
    # Get route and direction names
    route_name = route_info.get('route_name', 'Unknown')
    direction_name = direction_info.get('direction_name', 'Unknown')
    
    formatted_departure = {
        'scheduled_time': scheduled_time.strftime('%H:%M'),
        'live_time': None,
        'destination': destination,
        'platform': departure.get('platform_number', 'Unknown'),
        'at_platform': departure.get('at_platform', False),
        'vehicle': vehicle_info,
        'direction': direction_name,
        'disruptions': disruption_info,
        'route_name': route_name
    }
    
    if estimated_time_utc:
        try:
            estimated_time = datetime.fromisoformat(estimated_time_utc.replace('Z', '+00:00')).astimezone(LOCAL_TZ)
            formatted_departure['live_time'] = estimated_time.strftime('%H:%M')
        except Exception as e:
            logger.error(f"Error parsing estimated time {estimated_time_utc}: {e}")
    
    return formatted_departure

def fetch_departures():
    """
    Fetch departures from the transit API.
    
    Returns:
        list: List of formatted departure information
    """
    route_type = int(os.environ.get('ROUTE_TYPE', '0'))  # Default to train
    url = get_api_url(f"/v3/departures/route_type/{route_type}/stop/{STOP_ID}?expand=All&max_results=100")
    
    logger.info(f"Fetching from API: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            logger.error("API returned empty data")
            return []
            
        logger.info(f"API response contains keys: {', '.join(data.keys())}")
        
        routes = data.get('routes', {})
        directions = data.get('directions', {})
        runs = data.get('runs', {})
        disruptions = data.get('disruptions', {})
        
        departures = []
        raw_departures = data.get('departures', [])
        logger.info(f"Retrieved {len(raw_departures)} total departures from API")
        
        target_platform = os.environ.get('TARGET_PLATFORM')
        filtered_count = 0
        error_count = 0
        
        for departure in raw_departures:
            platform = str(departure.get('platform_number', ''))
            
            # Filter by platform if specified
            if target_platform and platform != target_platform:
                continue
                
            filtered_count += 1
            
            try:
                formatted_departure = parse_departure_data(
                    departure, routes, directions, runs, disruptions
                )
                departures.append(formatted_departure)
            except Exception as e:
                logger.error(f"Error parsing departure data: {e}")
                logger.error(f"Problematic departure data: {departure}")
                error_count += 1
        
        logger.info(f"Found {filtered_count} filtered departures, successfully parsed {len(departures)}, errors: {error_count}")
        
        departures.sort(key=lambda x: x['scheduled_time'])
        return departures
    
    except Exception as e:
        logger.error(f"Error fetching from API: {e}")
        if 'response' in locals():
            logger.error(f"Response status code: {response.status_code}")
            logger.error(f"Response text: {response.text[:500]}")
        return []

def lambda_handler(event, context):
    # AWS Lambda handler function
    try:
        logger.info("Starting Lambda execution")
        
        # Check for valid API credentials
        if not DEV_ID or not API_KEY:
            logger.error("Missing API credentials in environment variables")
            return {
                'statusCode': 500,
                'body': json.dumps('Missing API credentials')
            }
        
        # Fetch departures
        departures = fetch_departures()
        
        # Store in DynamoDB
        if departures:
            try:
                table.put_item(
                    Item={
                        'id': os.environ.get('DYNAMODB_ID', 'departures'),
                        'departures': departures,
                        'last_updated': datetime.now().isoformat()
                    }
                )
            except ClientError as e:
                logger.error(f"Error storing departures in DynamoDB: {e}")
                return {
                    'statusCode': 500,
                    'body': json.dumps('Error storing departures')
                }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully updated departures',
                'count': len(departures)
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda execution error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Lambda execution error: {str(e)}')
        } 