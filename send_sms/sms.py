import boto3
import time
import os
def sms_send(phone_number,message,key,access_key):
	client=boto3.client(
		"sns",
		aws_access_key_id=key,
		aws_secret_access_key=access_key,
		region_name="eu-west-1"


	)
	client.publish(
		PhoneNumber=phone_number,
		Message=message+"\nFrom Moriarty"

	)
