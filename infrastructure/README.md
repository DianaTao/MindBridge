# MindBridge Infrastructure (Python CDK)

This directory contains the AWS infrastructure as code for MindBridge AI, implemented using AWS CDK in Python.

## Prerequisites
- Python 3.8+
- [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html) (install with `pip install aws-cdk-lib constructs`)
- AWS CLI configured (`aws configure`)

## Setup

```bash
cd infrastructure
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Deploy

```bash
cdk synth   # Synthesize CloudFormation template
cdk deploy  # Deploy to AWS
```

## Useful Commands
- `cdk diff`   - Compare deployed stack with current code
- `cdk destroy` - Remove the stack from your AWS account

## Stack Entry Point
- The main stack is defined in `mindbridge-stack.py`. 