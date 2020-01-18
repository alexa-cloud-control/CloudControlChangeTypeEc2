""" Lambda function - change ec2 type """
import boto3

def cloud_control_change_type_ec2(event, context):
    """ Lambda function - change ec2 type """

    # validate instance name
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [event["body"]["InstanceName"]]
            }
        ]
    )
    instance_list = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_list.append(instance['InstanceId'])

    if not instance_list:
        msg = "I cannot find the instance with name {}.".format(event["body"]["InstanceName"])
        return {"msg": msg}

    try:
        ec2_client.stop_instances(InstanceIds=[instance_list[0]])
        if_stopped = ec2_client.get_waiter('instance_stopped')
        if_stopped.wait(InstanceIds=[instance_list[0]])
        ec2_client.modify_instance_attribute(
            InstanceId=instance_list[0],
            Attribute='instanceType',
            Value=event["body"]["NewType"])
        ec2_client.start_instances(InstanceIds=[instance_list[0]])
        msg = "Instance is back on-line."
        return {"msg": msg}
    except (SyntaxError, KeyError, NameError) as e_msg:
        msg = "An error occured during resizing! The reason is {}".format(
            str(e_msg)
        )
        return {"msg": msg}
