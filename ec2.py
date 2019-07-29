import boto3, datetime

def CheckTime(CurrentTime):
    TimeFormat = "%H:%M:%S"
    Time = CurrentTime.strftime(TimeFormat)
    
    if Time <= "07:59:00" or Time >= "19:59:00":
        return True
    else:
        return False	
        
def send_email(sub, BodyText):
        try:
                client = boto3.client('ses')
                response = client.send_email(
                    Source='yourmailid@example.com',
                    Destination={
                        'ToAddresses': ['yourmailid@example.com']
                    },
                    Message={
                        'Subject': {
                            'Data': sub,
                            'Charset': 'UTF-8'
                        },
                        'Body': {
                            #'Html': {
                            #    'Data': body,
                            #    'Charset': 'UTF-8'
                            #},
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
    sub = ""
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_instances()
    RequiredTags = ['owner', 'application', 'stack', '24/7', 'name']
    BodyText = ""
    for reservations in response['Reservations']:
            for instances in reservations['Instances']:
                    if instances['State']['Name'] != 'terminated':
                            t1_count = 0
                            t2_count = 0
                            lt_instance = instances['LaunchTime']
                            CurrentTime = datetime.datetime.now(lt_instance.tzinfo)+datetime.timedelta(hours=5.5)
                            four_hours_old = datetime.datetime.now(lt_instance.tzinfo)-datetime.timedelta(hours=4)
                            six_hours_old = datetime.datetime.now(lt_instance.tzinfo)-datetime.timedelta(hours=6)
                            twelve_hours_old = datetime.datetime.now(lt_instance.tzinfo)-datetime.timedelta(hours=12)
                            twelve_hours = lt_instance+datetime.timedelta(hours=12)
                            TagValue = {}
                            
                            DefaultTags = ""
                            if 'Tags' in instances:
                                    for tags in instances['Tags']:
                                            DefaultTags += "\t"+tags['Key']+" : "+tags['Value']+"\r"
                                            if 'application' == tags['Key'].lower().strip():
                                                    TagValue["application"] = tags['Value']
                                            elif 'owner' == tags['Key'].lower().strip():
                                                    TagValue["owner"] = tags['Value']
                                            elif 'stack' == tags['Key'].lower().strip():
                                                    TagValue["stack"] = tags['Value']
                                            elif 'name' == tags['Key'].lower().strip():
                                                    TagValue["name"] = tags['Value']
                                            elif '24/7' == tags['Key'].replace(" ", ""):
                                                    TagValue["24/7"] = tags['Value']
                                                    t2_count = 1 if 'true' in tags['Value'].lower().strip() else 2
                            if not DefaultTags:
                                DefaultTags = "\tEmpty"
                            t1_count = len(TagValue)
                            if t1_count < 5:
                                    BodyText += "Instance terminated due to insufficient tag information. \rInstance ID: " + instances['InstanceId'] + "\rAvailable Tags:\r" + DefaultTags + "\n\rRequired Tags:\rName\rApplication\rOwner\rStack\r24/7\n\r"
                                    modify_instance_response = ec2_client.modify_instance_attribute(DisableApiTermination={'Value':False}, InstanceId=instances['InstanceId'], DryRun=False)
                                    ec2_action_response = ec2_client.terminate_instances(InstanceIds=[instances['InstanceId']], DryRun=False)
                                    sub = "AWSCostOptimzation-EC2-Terminate"
                                    print(modify_instance_response)
                                    print(ec2_action_response)
                            elif t2_count == 2 and instances['State']['Name'] != 'stopped':
                                    
                                    if CheckTime(CurrentTime) is True:
                                            BodyText += "Instance will be shutdown between 20:00 to 08:00 IST because 24/7 is False.\r Instance ID: " + instances['InstanceId'] + "\rAvailable Tags:\r" +  DefaultTags + "\r"
                                            ec2_action_response = ec2_client.stop_instances(InstanceIds=[instances['InstanceId']], DryRun=False, Force=True)
                                            sub = "AWSCostOptimzation-EC2-Stop"
                                            print(ec2_action_response)
                            else:
                                    print("All tags are available for Instance ID: " + instances['InstanceId'])
            
    if sub: send_email(sub, BodyText)

