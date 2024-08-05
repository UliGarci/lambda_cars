import json
import boto3
import logging
from botocore.exceptions import ClientError
from decimal import Decimal

# Configura el logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CarsTable')

common_headers = {
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    return obj


def lambda_handler(event, context):
    try:
        logger.debug("Received event: %s", json.dumps(event))

        # Realiza la operación de escaneo en la tabla DynamoDB
        response = table.scan()
        logger.debug("DynamoDB scan response: %s", response)

        cars = response['Items']
        logger.debug("Items retrieved from DynamoDB: %s", cars)

        # Convierte los valores Decimal a float
        cars = decimal_to_float(cars)
        logger.debug("Items after conversion to float: %s", cars)

        if not cars:
            logger.info("No cars found.")
            return {
                'statusCode': 204,
                'body': json.dumps({'message': 'No hay carros registrados aun.'}),
                'headers': common_headers
            }

        return {
            'statusCode': 200,
            'body': json.dumps(cars),
            'headers': common_headers
        }

    except ClientError as e:
        logger.error("DynamoDB ClientError: %s", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'DynamoDB error', 'details': str(e)}),
            'headers': common_headers
        }

    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)}),
            'headers': common_headers
        }