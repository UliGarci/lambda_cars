import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CarsTable')


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
        response = table.scan()
        cars = response['Items']
        cars = decimal_to_float(cars)

        if not cars:
            return {
                'statusCode': 204,
                'body': json.dumps({'message': 'No hay carros registrados aun.'})
            }

        return {
            'statusCode': 200,
            'body': cars
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': {'error': 'DynamoDB error', 'details': str(e)}
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }