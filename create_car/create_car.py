import json
import boto3
import uuid
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CarsTable')


def lambda_handler(event, context):
    try:
        # Verifica que los campos requeridos estén presentes en el evento
        required_fields = ['nombre', 'tipo', 'potencia', 'capacidad']

        for field in required_fields:
            if field not in event:
                raise KeyError(field)

        car_id = str(uuid.uuid4())
        car = {
            'id': car_id,
            'nombre': event['nombre'],
            'tipo': event['tipo'],
            'potencia': event['potencia'],
            'capacidad': event['capacidad']
        }

        table.put_item(Item=car)

        response_body = {
            'message': 'Registro exitoso',
            'car': car
        }

        return {
            'statusCode': 200,
            'body': response_body,
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    except KeyError as e:
        response_body = {
            'error': 'Missing required fields',
            'details': str(e)
        }
        return {
            'statusCode': 400,
            'body': response_body,
            'headers': {
                'Content-Type': 'application/json'
            }
        }