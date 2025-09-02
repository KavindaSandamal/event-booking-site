# GitHub Webhook Setup for Jenkins

## Step 1: Get Jenkins Webhook URL
Your Jenkins webhook URL is:
```
https://391d189c015a.ngrok-free.app/github-webhook/
```

## Step 2: Configure GitHub Webhook

1. Go to your GitHub repository: `event-booking-platform`
2. Click **Settings** → **Webhooks** → **Add webhook**
3. Fill in the details:
   - **Payload URL**: `https://391d189c015a.ngrok-free.app/github-webhook/`
   - **Content type**: `application/json`
   - **Secret**: (optional, but recommended)
   - **Events**: Select "Just the push event" or "Send me everything"
   - **Active**: ✅ Checked

## Step 3: Test the Webhook

1. Make a small change to any file in your repository
2. Commit and push the changes
3. Check Jenkins for the triggered build

## Step 4: Jenkins Job Configuration

1. In Jenkins, create a new **Pipeline** job
2. Name it: `event-booking-platform`
3. In **Pipeline** section:
   - **Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: Your GitHub repository URL
   - **Branch**: `*/main` (or your default branch)
   - **Script Path**: `Jenkinsfile`

## Step 5: Required Jenkins Plugins

Make sure these plugins are installed:
- GitHub Integration Plugin
- Docker Pipeline Plugin
- Kubernetes Plugin
- Pipeline Plugin
- Git Plugin

## Step 6: Jenkins Credentials (if needed)

If you need to access private repositories:
1. Go to **Manage Jenkins** → **Manage Credentials**
2. Add GitHub credentials (username/password or token)

## Troubleshooting

- If webhook fails, check ngrok status: `http://127.0.0.1:4040`
- If Jenkins can't access minikube, ensure kubectl config is available
- Check Jenkins logs for detailed error messages
