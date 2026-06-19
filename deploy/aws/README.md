# AWS Deployment Guide

This project supports AWS deployment using **Amazon EKS** (Kubernetes) or **Amazon ECS** (containers).

## Option A: Amazon EKS

1. Build and push images to Amazon ECR:

```bash
aws ecr create-repository --repository-name traffic-backend
aws ecr create-repository --repository-name traffic-frontend
aws ecr create-repository --repository-name traffic-inference

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -f Dockerfile.backend -t traffic-backend .
docker tag traffic-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/traffic-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/traffic-backend:latest
```

2. Create an EKS cluster (example with `eksctl`):

```bash
eksctl create cluster --name traffic-cluster --region us-east-1 --nodes 2
```

3. Update image references in `k8s/stack.yaml` to your ECR URLs, then deploy:

```bash
kubectl apply -f k8s/stack.yaml
kubectl get svc -n traffic-system traffic-frontend
```

4. Use an AWS Application Load Balancer Ingress (optional) in front of the frontend LoadBalancer service.

## Option B: Amazon ECS Fargate

Use `deploy/aws/ecs-task-definition.json` as a starting point:

```bash
aws ecs register-task-definition --cli-input-json file://deploy/aws/ecs-task-definition.json
aws ecs create-cluster --cluster-name traffic-cluster
aws ecs create-service --cluster traffic-cluster --service-name traffic-backend --task-definition traffic-backend --desired-count 1
```

## Required AWS resources

| Resource | Purpose |
|----------|---------|
| ECR | Container image registry |
| EKS or ECS | Container orchestration |
| DocumentDB or MongoDB Atlas | Traffic event storage |
| Amazon MQ or self-hosted Mosquitto on ECS | MQTT broker |
| Application Load Balancer | Public dashboard/API access |
| CloudWatch | Logs and metrics |

## Environment variables

Set these in ECS task definitions or Kubernetes manifests:

- `MONGO_URI`
- `MQTT_BROKER`
- `INFERENCE_URL`
- `SIMULATE_SENSORS=0` in production (use real sensors)
- `VITE_API_BASE_URL` for frontend build/runtime

## Security

- Store secrets in AWS Secrets Manager
- Enable TLS on MQTT (port 8883) and HTTPS on the load balancer
- Restrict security groups to required ports only
