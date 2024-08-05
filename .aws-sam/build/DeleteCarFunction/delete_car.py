import json
import boto3
import logging
from botocore.exceptions import ClientError

# Configura el logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CarsTable')

def lambda_handler(event, context):
    try:
        # Registra el evento recibido
        logger.debug(f"Received event: {json.dumps(event)}")

        # Obtén el ID del parámetro de la ruta
        car_id = event['pathParameters']['id']
        logger.debug(f"Car ID: {car_id}")

        if not car_id:
            logger.warning("Missing path parameter: id")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing path parameter: id'})
            }

        # Intenta eliminar el elemento
        response = table.delete_item(
            Key={'id': car_id},
            ConditionExpression="attribute_exists(id)"
        )
        logger.info(f"Delete response: {response}")

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Carro eliminado exitosamente'})
        }

    except ClientError as e:
        logger.error(f"DynamoDB ClientError: {e}")
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
        logger.error(f"KeyError: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing path parameter', 'details': str(e)})
        }

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }