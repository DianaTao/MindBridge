# MindBridge CI/CD Pipeline Setup

This document describes the comprehensive CI/CD pipeline setup for the MindBridge application using GitHub Actions.

## 🚀 Overview

The CI/CD pipeline automates the entire deployment process including:
- **Code Quality Checks**: Linting, testing, and type checking
- **Security Scanning**: Vulnerability detection with Trivy
- **Infrastructure Deployment**: AWS CDK stack deployment
- **Frontend Deployment**: React app build and S3/CloudFront deployment
- **Lambda Function Deployment**: Automated Lambda function updates
- **Post-Deployment Testing**: Health checks and validation

## 📁 Pipeline Structure

```
.github/workflows/
├── ci-cd.yml              # Main CI/CD pipeline for deployments
└── pull-request.yml       # PR-specific checks (no deployment)
```

## 🔧 Configuration Files

### Python Tools
- `.flake8` - Flake8 linting configuration
- `pyproject.toml` - Black, pytest, mypy, and coverage configuration

### Frontend Tools
- `frontend/.eslintrc.js` - ESLint configuration
- `frontend/.prettierrc` - Prettier formatting rules

### Deployment
- `scripts/deploy.sh` - Local deployment script

## 🏗️ Pipeline Jobs

### 1. Lint and Test (`lint-and-test`)
**Triggers**: All pushes and pull requests
- Frontend linting and testing
- Python linting (flake8, black)
- Python testing with coverage
- Uploads coverage reports to Codecov

### 2. Build Frontend (`build-frontend`)
**Triggers**: Push to main/develop branches
- Builds React application for production
- Uploads build artifacts for later deployment

### 3. Deploy Infrastructure (`deploy-infrastructure`)
**Triggers**: Push to main/develop branches
- Deploys AWS CDK stack
- Sets environment context (dev/prod)
- Retrieves S3 bucket names from CloudFormation outputs

### 4. Deploy Frontend (`deploy-frontend`)
**Triggers**: Push to main/develop branches
- Syncs build files to S3 bucket
- Invalidates CloudFront cache
- Sets proper cache headers

### 5. Deploy Lambda Functions (`deploy-lambda-functions`)
**Triggers**: Push to main/develop branches
- Creates deployment packages for each Lambda function
- Updates Lambda function code
- Handles dependencies from requirements.txt

### 6. Post-Deployment Tests (`post-deployment-tests`)
**Triggers**: Push to main/develop branches
- Tests health endpoints
- Validates frontend accessibility
- Provides deployment success notification

### 7. Security Scan (`security-scan`)
**Triggers**: Push to main branch only
- Runs Trivy vulnerability scanner
- Uploads results to GitHub Security tab

## 🔐 Required GitHub Secrets

Configure these secrets in your GitHub repository settings:

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_ACCOUNT_ID=your_account_id

# Frontend Environment Variables
REACT_APP_API_URL=https://your-api-gateway-url.execute-api.region.amazonaws.com
REACT_APP_WS_URL=wss://your-websocket-url.execute-api.region.amazonaws.com
```

## 🚀 Local Deployment

Use the provided deployment script for local development:

```bash
# Deploy everything to development
./scripts/deploy.sh

# Deploy to production
./scripts/deploy.sh -e prod

# Deploy only frontend
./scripts/deploy.sh -f

# Deploy only infrastructure
./scripts/deploy.sh -i

# Deploy only Lambda functions
./scripts/deploy.sh -l

# Run tests only
./scripts/deploy.sh -t
```

## 📋 Prerequisites

### Local Development
- AWS CLI configured with appropriate permissions
- Node.js 18+ and npm
- Python 3.11+
- AWS CDK CLI

### GitHub Actions
- Repository secrets configured
- AWS IAM user with deployment permissions

## 🔄 Workflow Triggers

### Automatic Triggers
- **Push to main**: Full deployment to production
- **Push to develop**: Full deployment to development
- **Pull Request**: Code quality checks only

### Manual Triggers
You can manually trigger workflows from the GitHub Actions tab:
- `ci-cd.yml` - Full deployment pipeline
- `pull-request.yml` - Code quality checks

## 🛡️ Security Features

### Code Quality
- ESLint for JavaScript/TypeScript
- Flake8 and Black for Python
- TypeScript type checking
- Test coverage reporting

### Security Scanning
- Trivy vulnerability scanner
- GitHub Security tab integration
- Dependency vulnerability detection

### Infrastructure Security
- CDK security best practices
- IAM least privilege principles
- CloudFormation drift detection

## 📊 Monitoring and Logs

### GitHub Actions
- View pipeline status in Actions tab
- Download build artifacts
- Review security scan results

### AWS CloudWatch
- Lambda function logs
- API Gateway access logs
- CloudFront access logs

### Health Checks
- Automated post-deployment testing
- Health endpoint validation
- Frontend accessibility checks

## 🔧 Customization

### Environment-Specific Configuration

The pipeline uses CDK context for environment-specific settings:

```bash
# Development
cdk deploy --context environment=development

# Production
cdk deploy --context environment=production
```

### Adding New Lambda Functions

1. Create the function directory in `lambda_functions/`
2. Add deployment entry in `scripts/deploy.sh`
3. Update the GitHub Actions workflow if needed

### Frontend Environment Variables

Add new environment variables to:
1. GitHub repository secrets
2. Frontend build step in CI/CD
3. Local deployment script

## 🚨 Troubleshooting

### Common Issues

1. **CDK Bootstrap Required**
   ```bash
   cd infrastructure
   cdk bootstrap
   ```

2. **AWS Credentials Not Configured**
   ```bash
   aws configure
   ```

3. **Node.js Version Mismatch**
   - Update Node.js to version 18+
   - Clear npm cache: `npm cache clean --force`

4. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install flake8 black pytest pytest-cov mypy
   ```

### Debug Commands

```bash
# Check AWS configuration
aws sts get-caller-identity

# Validate CDK stack
cd infrastructure && cdk synth

# Test Lambda function locally
aws lambda invoke --function-name function-name response.json

# Check CloudFormation stack status
aws cloudformation describe-stacks --stack-name MindBridgeStack
```

## 📈 Best Practices

### Code Quality
- Write tests for new features
- Maintain high test coverage
- Use TypeScript for frontend
- Follow linting rules

### Security
- Regularly update dependencies
- Review security scan results
- Use least privilege IAM policies
- Enable CloudTrail logging

### Deployment
- Test in development first
- Use feature branches for new features
- Monitor deployment logs
- Set up alerts for failures

## 🔗 Related Documentation

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [React Deployment Guide](https://create-react-app.dev/docs/deployment/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

## 🤝 Contributing

When contributing to the CI/CD pipeline:

1. Test changes locally first
2. Update documentation
3. Follow existing patterns
4. Add appropriate error handling
5. Consider security implications

## 📞 Support

For issues with the CI/CD pipeline:

1. Check the troubleshooting section
2. Review GitHub Actions logs
3. Verify AWS credentials and permissions
4. Test locally with the deployment script
5. Create an issue with detailed error information 