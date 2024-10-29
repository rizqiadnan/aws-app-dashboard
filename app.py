# app.py
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import os
import boto3
import plotly
import plotly.graph_objs as go
import json
from aws_manager import list_ec2_instances, get_cloudwatch_metrics

# Load environment variables from .env file
load_dotenv()

# Initialize AWS clients using environment variables
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

# Define AWS clients here
ec2_client = session.client('ec2')
cloudwatch_client = session.client('cloudwatch')

app = Flask(__name__)

@app.route('/')
def home():
    instances = list_ec2_instances(ec2_client)  # Pass ec2_client as an argument
    return render_template('dashboard.html', instances=instances)

@app.route('/metrics/<instance_id>')
def metrics(instance_id):
    metric_data = get_cloudwatch_metrics(cloudwatch_client, instance_id)  # Pass cloudwatch_client as an argument
    fig = go.Figure([go.Scatter(y=metric_data, mode='lines', name="CPU Utilization")])
    fig.update_layout(title="EC2 Instance CPU Utilization",
                      xaxis_title="Time (last hour)",
                      yaxis_title="CPU %")
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('dashboard.html', graph_json=graph_json)

if __name__ == '__main__':
    app.run(debug=True)
