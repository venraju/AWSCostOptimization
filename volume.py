import boto3, datetime

def send_email(sub, BodyText):
        try:
                client = boto3.client('ses')
                response = client.send_email(
                    Source='coreservicesteam@morningstar.com',
                    Destination={
                        'ToAddresses': ['coreservicesteam@morningstar.com']
                    },
                    Message={
                        'Subject': {
                            'Data': sub,
                            'Charset': 'UTF-8'
                        },
                        'Body': {
                            'Text': {
                                'Charset': 'UTF-8',
                                'Data': BodyText
                            },
                        },
                    },
                    Tags=[
                        {
                            'Name': 'Mail',
                            'Value': 'Test'
                        },
                    ]
                )
        except Exception as e:
                print(e.response['Error']['Message'])
        else:
                print("Email sent! Message ID:"),
                print(response['MessageId'])


def lambda_handler(event, context):
        client = boto3.client('ec2')
        response = client.describe_volumes()
        sub = BodyText = ""
        BodyTitle = "List of unused volumes.\n\r"
        for Volumes in response['Volumes']:
                if not Volumes['Attachments']:
                        sub = "AWSCostOptimzation-EC2-IdleVolumes-Stop"
                        lt_volume = Volumes['CreateTime']
                        BodyText += "ID: %s \rType: %s \rSize: %s \rCreate Time: %s \n\r" % (Volumes['VolumeId'], Volumes['VolumeType'], Volumes['Size'], lt_volume.strftime("%c %Z"))

        if sub: send_email(sub, BodyTitle+BodyText)
