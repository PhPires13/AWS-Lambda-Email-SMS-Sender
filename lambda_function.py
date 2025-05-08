import boto3
import json
import logging

ses_client = boto3.client('ses')
sns_client = boto3.client('sns')

def send_email(body):
    source_email = body["from"]
    to_emails = body["to"]
    title = body["title"]
    message = body["message"]

    return ses_client.send_email(
        Source=source_email,
        Destination={
            'ToAddresses': to_emails
        },
        Message={
            'Subject': {
                'Data': title,
            },
            'Body': {
                'Text': {
                    'Data': message
                },
                'Html': {
                    'Data': message
                }
            }
        }
    )

def send_sms(body):
    sender = body["sender"]
    phone_number = body["phone_number"]
    message = body["message"]

    return sns_client.publish(
        PhoneNumber=phone_number,
        Message=message,
        MessageAttributes={
            'AWS.SNS.SMS.SenderID': {
                'DataType': 'String',
                'StringValue': sender
            },
            'AWS.SNS.SMS.SMSType': {
                'DataType': 'String',
                'StringValue': 'Promotional'  # 'Promotional' tends to incur lower costs than 'Transactional'
            }
        }
    )

def prepare_response(status_code: int, body: any) -> dict:
    return {
        'statusCode': status_code,
        'body': json.dumps(body)
    }

def lambda_handler(event, context):
    logging.info(event)
    body = json.loads(event["body"])
    try:
        action = body["action"]
        if action == 'email':
            response = send_email(body)
        elif action == 'sms':
            response = send_sms(body)
        else:
            raise KeyError('Invalid action: ' + action)

        return prepare_response(200, response)
    except KeyError as e:
        return prepare_response(400, e)
    except Exception as e:
        logging.error(e)
        return prepare_response(500, e)
