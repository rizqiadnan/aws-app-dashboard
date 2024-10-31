#
import os
import boto3
import plotly.graph_objs as go

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from models import db, User
from aws_manager import list_ec2_instances, get_cloudwatch_metrics

# Create a Blueprint for routes
main = Blueprint('main', __name__)

# Initialize AWS clients
def create_aws_clients():
    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )
    return {
        'ec2': session.client('ec2'),
        'rds': session.client('rds'),
        'cloudwatch': session.client('cloudwatch')
    }

aws_clients = create_aws_clients()

@main.route('/')
@login_required  # Protect the home route
def home():
    instances = list_ec2_instances(aws_clients['ec2'])
    return render_template('dashboard.html', instances=instances)

@main.route('/metrics/<instance_id>')
@login_required
def metrics(instance_id):
    metric_data = get_cloudwatch_metrics(aws_clients['cloudwatch'], instance_id)
    fig = create_cpu_utilization_chart(metric_data)
    graph_json = fig.to_json()
    return render_template('dashboard.html', graph_json=graph_json)

def create_cpu_utilization_chart(metric_data):
    fig = go.Figure(data=[go.Scatter(y=metric_data, mode='lines', name="CPU Utilization")])
    fig.update_layout(title="EC2 Instance CPU Utilization", xaxis_title="Time", yaxis_title="CPU Utilization (%)")
    return fig

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # In a real app, use hashed passwords
            login_user(user)
            return redirect(url_for('main.home'))
        flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))