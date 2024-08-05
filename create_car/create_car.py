import json
import boto3
import uuid
import logging
from botocore.exceptions import ClientError

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CarsTable')
common_headers = {
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}
def lambda_handler(event, context):
    logger.debug("Lambda handler started.")
    logger.debug("Event received: %s", event)

    try:
        # Verifica que el cuerpo de la solicitud esté presente
        body = json.loads(event.get('body', '{}'))  # Deserializa el cuerpo del evento
        logger.debug("Parsed body: %s", body)

        # Verifica que los campos requeridos estén presentes en el cuerpo
        required_fields = ['nombre', 'tipo', 'potencia', 'capacidad']
        logger.debug("Checking required fields: %s", required_fields)

        for field in required_fields:
            if field not in body:
                logger.error("Missing required field: %s", field)
                raise KeyError(field)

        car_id = str(uuid.uuid4())
        car = {
            'id': car_id,
            'nombre': body['nombre'],
            'tipo': body['tipo'],
            'potencia': body['potencia'],
            'capacidad': body['capacidad']
        }
        logger.debug("Creating car record: %s", car)

        table.put_item(Item=car)
        logger.info("Car record successfully inserted into DynamoDB.")

        response_body = {
            'message': 'Registro exitoso',
            'car': car
        }

        return {
            'statusCode': 200,
            'body': json.dumps(response_body),
            'headers': common_headers
        }

    except KeyError as e:
        logger.error("KeyError occurred: %s", str(e))
        response_body = {
            'error': 'Missing required fields',
            'details': str(e)
        }
        return {
            'statusCode': 400,
            'body': json.dumps(response_body),
            'headers': common_headers
        }

    except ClientError as e:
        logger.error("ClientError occurred: %s", str(e))
        response_body = {
            'error': 'Error en la operación de DynamoDB',
            'details': str(e)
        }
        return {
            'statusCode': 500,
            'body': json.dumps(response_body),
            'headers': common_headers
        }

    except Exception as e:
        logger.error("Exception occurred: %s", str(e))
        response_body = {
            'error': 'Error interno del servidor',
            'details': str(e)
        }
        return {
            'statusCode': 500,
            'body': json.dumps(response_body),
            'headers': common_headers
        }