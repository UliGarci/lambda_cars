import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CarsTable')


def lambda_handler(event, context):
    try:
        car_id = event['pathParameters']['id']

        if not car_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing path parameter: id'})
            }

        response = table.delete_item(
            Key={'id': car_id},
            ConditionExpression="attribute_exists(id)"
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Carro eliminado exitosamente'})
        }

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Car not found'})
            }
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'DynamoDB error', 'details': str(e)})
        }

    except KeyError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing path parameter', 'details': str(e)})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }