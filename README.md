# AWSCostOptimization
AWS Cost Optimization Techniques
------------
## 1. Purpose
To manage the AWS cost efficiently and set the process for governance on spending. This will also allow us to shutdown or delete unused services not following the standard process (Pay as you go)


## 2. Implementation
All python files in this repository are lambda code. To implement this in aws, you just needs to copy the code to a lamda function and create a cloudwatch event to execute it.


## 3. Logic & Implementation of code
### 3.1 EC2_Scan.py
#### 3.1.1 Logic
- Scan EC2 instances
- Check whether the required tags are available
	- Required tags:
			- Name: Insance Name
			- Owner: Name of the Engineer or Service owner  
			- Application: Name of the Application (Ex. Graphite)
			- 24/7: True/False (Whether machine is expected to run 24/7)
			- Stack: Environment (Test,Stg, Prod etc)  
- If anyone of the listed tag is not available in existing instance then that instance will be deleted
- If all tags are available and **24/7** is set False then that instance will be shutdown between 8:00 PM to 8:00 AM IST. 
- If all tags are available and **24/7** is set True then no action will be taken on it.
- Finaly a mail will be send to yourmailid@example.com, if any action taken on any instance.

#### 3.1.2 Lamda Function in AWS
Function Name: EC2_Scan

#### 3.1.3 CloudWatch
Rule Name: EC2_Scan_Rule
Schedule: Fixed rate of 2 hours 

### 3.2 Volume_Scan.py
#### 3.2.1 Logic
- Scan the volumes
- List all the volumes which are not attached to any instance.
- If any volume found not attached to any instance then a mail will be send to yourmailid@example.com with the volume details.

#### 3.2.2 Lambda Function in AWS
Function Name: Volume_Scan

#### 3.1.3 CloudWatch
Rule Name: EC2_Scan_Rule
Schedule: Every Monday, 08:00 AM

### 3.3 ELB_Scan.py
#### 3.3.1 Logic
- Frist stage, Scan Load Balancer
- Load balancer which does not have proper tags and not listening to any target or instance that load balancer will be deleted.
	- Required tags:
			- Name: Insance Name
			- Owner: Name of the Engineer or Service owner  
			- Application: Name of the Application (Ex. Graphite)
			- Stack: Environment (Test,Stg, Prod etc)  
- Second stage, Scan Target Group
- Target group which does not have proper tags and does not have target in it that target group will be deleted.
- Finally, if any action taken in Load Balancer or Target Group then a mail will be send to yourmailid@example.com. 

### 3.3.2 Lambda Function in AWS
Function Name: ELB_Scan

### 3.3.3 CloudWatch
Rule Name: ELB_Scan_Rule
Schedule: Fixed rate of 2 hours
