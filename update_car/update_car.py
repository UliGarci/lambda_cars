import json
import boto3
import logging
from botocore.exceptions import ClientError

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
def lambda_handler(event, context):
    try:
        logger.debug("Received event: %s", json.dumps(event))

        # Obtener el ID del carro desde los parámetros de la ruta
        car_id = event.get('pathParameters', {}).get('id')
        logger.debug("Car ID: %s", car_id)

        if not car_id:
            logger.warning("Missing path parameter: ID is required")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing path parameter', 'details': 'ID is required'}),
                'headers': common_headers
            }

        # Obtener el cuerpo de la solicitud
        body = json.loads(event.get('body', '{}'))
        logger.debug("Request body: %s", body)

        # Verificar que todos los campos requeridos estén presentes
        required_fields = ['nombre', 'tipo', 'potencia', 'capacidad']
        missing_fields = [field for field in required_fields if field not in body]

        if missing_fields:
            logger.warning("Missing required fields: %s", ', '.join(missing_fields))
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields', 'details': ', '.join(missing_fields)}),
                'headers': common_headers
            }

        # Preparar la expresión de actualización y los valores de atributos
        update_expression = "set "
        expression_attribute_values = {
            ':n': body['nombre'],
            ':t': body['tipo'],
            ':p': body['potencia'],
            ':c': body['capacidad']
        }

        update_expression += "nombre = :n, tipo = :t, potencia = :p, capacidad = :c"
        logger.debug("Update expression: %s", update_expression)
        logger.debug("Expression attribute values: %s", expression_attribute_values)

        # Realiza la actualización en DynamoDB
        table.update_item(
            Key={'id': car_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

        logger.info("Car updated successfully")
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Carro actualizado correctamente'}),
            'headers': common_headers
        }

    except json.JSONDecodeError as e:
        logger.error("JSON Decode Error: %s", e)
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON format', 'details': str(e)}),
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