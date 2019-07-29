import boto3, datetime, time

ListTargetGroupInc = 1
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

def ResourceTags(TagsRes):
	RequiredTags = ['owner', 'application', 'stack', 'name']
	TagValue = {}
	TagCount = 0
	DefaultTags = "\r"

	if 'Tags' in TagsRes['TagDescriptions'][0]:
		for Tag in TagsRes['TagDescriptions'][0]['Tags']:
			DefaultTags += "\t"+Tag['Key']+":"+Tag['Value']+"\r"
			if 'application' == Tag['Key'].lower().strip():
			        TagValue["application"] = Tag['Value']
			elif 'owner' == Tag['Key'].lower().strip():
			        TagValue["owner"] = Tag['Value']
			elif 'stack' == Tag['Key'].lower().strip():
			        TagValue["stack"] = Tag['Value']
			elif 'name' == Tag['Key'].lower().strip():
			        TagValue["name"] = Tag['Value']
			
		if len(RequiredTags) == len(TagValue):
			return True, DefaultTags.rstrip('\r')
			
	if DefaultTags == "\r":
		DefaultTags = "Empty"
	return False, DefaultTags.rstrip('\r')

def TargetGroupFunc(TargetGroupArnValue):
	
	global ListTargetGroupInc
	Message = ""
	elbv2_client = boto3.client('elbv2')
	TagsRes = elbv2_client.describe_tags(ResourceArns=[TargetGroupArnValue])
	TagStatus, DefaultTags = ResourceTags(TagsRes)
	TargetGroupHealthRes = elbv2_client.describe_target_health(TargetGroupArn=TargetGroupArnValue)
	InstanceId = [x['Target']['Id'] for x in TargetGroupHealthRes['TargetHealthDescriptions'] if x['Target']['Id']]
	#print(TargetGroupHealthRes)
	if TagStatus is False or not TargetGroupHealthRes['TargetHealthDescriptions']:
		Message += "\r\r" + str(ListTargetGroupInc) + ")\rTarget Group Arn : " + TargetGroupArnValue + "\rTarget: " + str(InstanceId) + "\rTags :" + DefaultTags
		try:
		    ListTargetGroupInc += 1
			TargetGroupDeleteRes = elbv2_client.delete_target_group(TargetGroupArn=TargetGroupArnValue)
			Message += "\rStatus: TargetGroup Deleted Successfully."
			print("Deleted TargetGroup: " + TargetGroupArnValue)
			time.sleep(25)
		except:
			ListTargetGroupInc += -1
			#print(TargetGroupDeleteRes)
			Message += "\rStatus: Failed to delete TargetGroup"
			print("Delete TargetGroup Failed: " + TargetGroupArnValue)

	return Message
		
def lambda_handler(event, context):
    
    sub="AWSCostOptimization-ELB-Terminate"
    Body = TargetGroupMesg = LoadBalancerMesg = ""
    ListLoadBalancerInc = 1
    
    elb_client = boto3.client('elb')
    LoadBalancerRes = elb_client.describe_load_balancers()
    for ClassicLB in LoadBalancerRes['LoadBalancerDescriptions']:
        TagsRes = elb_client.describe_tags(LoadBalancerNames=[ClassicLB['LoadBalancerName']])
        TagStatus, DefaultTags = ResourceTags(TagsRes)
        if  TagStatus is False or not ClassicLB['Instances']:
            ClassicInstance = "Empty"
            if ClassicLB['Instances']:
            	ClassicInstance = [x['InstanceId'] for x in ClassicLB['Instances']]
            ClassicLBCreatedTime = ClassicLB['CreatedTime'].strftime("%c %Z")
            LoadBalancerMesg += "\r\r" + str(ListLoadBalancerInc) + ")\rLoadBalancer Name: " + ClassicLB['LoadBalancerName'] +"\rType: Classic\rCreate Time: "+ ClassicLBCreatedTime +"\rInstances: " + str(ClassicInstance) + "\rTags: " + DefaultTags
            try:
                ListLoadBalancerInc += 1
            	LoadBalancerDeleteRes = elb_client.delete_load_balancer(LoadBalancerName=ClassicLB['LoadBalancerName'])
            	LoadBalancerMesg += "\rStatus: LoadBalancer Deleted Successfully"
            	print("Deleted Classic LoadBalancer: " + ClassicLB['LoadBalancerName'])
            	time.sleep(25)
            except:
                ListLoadBalancerInc += -1
                print("Delete Classic LoadBalancer Failed: " + ClassicLB['LoadBalancerName'])
                LoadBalancerMesg += "\rStatus: Failed To Delete Classic LoadBalancer."
            	
    elbv2_client = boto3.client('elbv2')
    LoadBalancerRes = elbv2_client.describe_load_balancers()
    for LoadBalancer in LoadBalancerRes['LoadBalancers']:
    	TagsRes = elbv2_client.describe_tags(ResourceArns=[LoadBalancer['LoadBalancerArn']])
    	ListenerRes = elbv2_client.describe_listeners(LoadBalancerArn=LoadBalancer['LoadBalancerArn'])
    	LBCreatedTime = LoadBalancer['CreatedTime'].strftime("%c %Z")
    	TagStatus, DefaultTags = ResourceTags(TagsRes)
    	ListenerCount = TargetGroupCheck = 0
    	
    	TargetArn = "\r"
    	ListenerArn = "\r"
    	if ListenerRes['Listeners']:
    		ListenerCount = len(ListenerRes['Listeners'])
    		for Listener in ListenerRes['Listeners']:
    			ListenerArn += "\t" + Listener['ListenerArn'] + "\r"
    			if 'TargetGroupArn' in Listener['DefaultActions'][0]:
    				TargetGroupArn = Listener['DefaultActions'][0]['TargetGroupArn']
    				TagsRes = elbv2_client.describe_tags(ResourceArns=[TargetGroupArn])
    				TargetTagStatus, TargetDefaultTags = ResourceTags(TagsRes)
    				TargetGroupHealthRes = elbv2_client.describe_target_health(TargetGroupArn=TargetGroupArn)
    				if TagStatus is False or not TargetGroupHealthRes['TargetHealthDescriptions']:
    					TargetGroupCheck += 1 
    					TargetArn += "\t" + TargetGroupArn + "\r"
    			else:
    				TargetArn += "\tEmpty\r"
    	else:
    		ListenerArn = "\tEmpty\r"
    		TargetArn += "\tEmpty\r"
    					
    	if TagStatus is False or TargetGroupCheck == ListenerCount  or not ListenerRes['Listeners'] :
    		LoadBalancerMesg += "\r\r" + str(ListLoadBalancerInc) + ")\rLoad Balancer Name: " + LoadBalancer['LoadBalancerName'] + "\rType: " + LoadBalancer['Type'] +"\rTags: " + DefaultTags  + "\rLoad Balancer ARN: \r\t" + LoadBalancer['LoadBalancerArn'] + "\rListener Arn: " + ListenerArn.rstrip('\r') + "\rTarget Group Arn: " + TargetArn.rstrip('\r') +" \rCreate Time: "+ LBCreatedTime 
    		try:
    		    ListLoadBalancerInc += 1
    			LoadBalancerDeleteRes = elbv2_client.delete_load_balancer(LoadBalancerArn=LoadBalancer['LoadBalancerArn'])
    			LoadBalancerMesg += "\rStatus: LoadBalancer Deleted Successfully"
    			print("Deleted LoadBalancer: "  + LoadBalancer['LoadBalancerArn'])
    			time.sleep(25)
    		except:
    			ListLoadBalancerInc += -1
    			print("Delete LoadBalancer Failed: "  + LoadBalancer['LoadBalancerArn'])
    			LoadBalancerMesg += "\rStatus: Failed To Delete LoadBalancer"

    TargetGroupResponse = elbv2_client.describe_target_groups()
    for TargetGroups in TargetGroupResponse['TargetGroups']:
    	print(TargetGroups['TargetGroupArn'])
    	TargetGroupMesg += TargetGroupFunc(TargetGroups['TargetGroupArn'])
    	
    if LoadBalancerMesg:
    	Body += "  -------------- List of Deleted LoadBalancer --------------" + LoadBalancerMesg
    if TargetGroupMesg:
    	Body += "\r\r  -------------- List of Deleted TargetGroup --------------" + TargetGroupMesg
    if Body: send_email(sub, Body)
