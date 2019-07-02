import boto3

ec2 = boto3.client('ec2', region_name='us-west-2')

print(ec2.describe_instances())
