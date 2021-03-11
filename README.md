# ml-workshop-examples

This repo contains code and workshop examples for using machine learning on AWS

## To begin
Open CloudShell and paste in the following commands:
```
curl -O https://raw.githubusercontent.com/ueberhund/ml-workshop-examples/main/cloud9-setup.yml

aws cloudformation create-stack --stack-name C9-Observability-Workshop --template-body file://cloud9-cfn.yaml --capabilities CAPABILITY_NAMED_IAM

aws cloudformation wait stack-create-complete --stack-name C9-Observability-Workshop

echo -e "Cloud9 Instance is Ready!!\n\n"
```