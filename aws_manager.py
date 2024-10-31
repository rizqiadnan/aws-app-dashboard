# aws_manager.py

from datetime import datetime, timedelta

def list_ec2_instances(ec2_client):
    """Retrieve a list of all EC2 instances."""
    response = ec2_client.describe_instances()
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append({
                'InstanceId': instance['InstanceId'],
                'InstanceType': instance['InstanceType'],
                'State': instance['State']['Name'],
                'Architecture': instance['Architecture'],
                # 'LaunchTime': instance['LaunchTime']
            })
    return instances

def get_cloudwatch_metrics(cloudwatch_client, instance_id):
    """Retrieve CPUUtilization metrics for a specific EC2 instance."""
    now = datetime.utcnow()
    response = cloudwatch_client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'cpuUtilization',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/EC2',
                        'MetricName': 'CPUUtilization',
                        'Dimensions': [
                                {
                                    'Name': 'InstanceId',
                                    'Value': instance_id
                            }
                        ]
                    },
                    'Period': 300,
                    'Stat': 'Average'
                },
                'ReturnData': True
            },
        ],
        StartTime=now - timedelta(hours=2),
        EndTime=now
    )
    return response['MetricDataResults'][0]['Values']
