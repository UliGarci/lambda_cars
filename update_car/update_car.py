import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CarsTable')


def lambda_handler(event, context):
    try:
        # Obtener el ID del carro desde los parámetros de la ruta
        car_id = event.get('pathParameters', {}).get('id')

        if not car_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing path parameter', 'details': 'ID is required'}),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }

        # Obtener el cuerpo de la solicitud
        body = json.loads(event.get('body', '{}'))

        # Verificar que todos los campos requeridos estén presentes
        required_fields = ['nombre', 'tipo', 'potencia', 'capacidad']
        missing_fields = [field for field in required_fields if field not in body]

        if missing_fields:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields', 'details': ', '.join(missing_fields)}),
                'headers': {
                    'Content-Type': 'application/json'
                }
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

        # Realiza la actualización en DynamoDB
        table.update_item(
            Key={'id': car_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Carro actualizado correctamente'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    except json.JSONDecodeError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON format', 'details': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'DynamoDB error', 'details': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }