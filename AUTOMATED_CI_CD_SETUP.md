# 🚀 Automated CI/CD Setup Guide

## Overview
This guide will help you set up **automatic CI/CD** that triggers on every Git push to your repository.

## Current Status
- ✅ Jenkins is running and accessible at `http://jenkins.event-booking.local`
- ✅ Pipeline is configured and working
- ✅ All services are deployed and running

## Option 1: GitHub Webhook (Recommended)

### Step 1: Configure Jenkins for Webhooks

1. **Access Jenkins**: Go to `http://jenkins.event-booking.local`
2. **Login**: Use your Jenkins credentials
3. **Go to your pipeline**: Click on "event-booking-git-pipeline"
4. **Configure**: Click "Configure" in the left sidebar
5. **Build Triggers**: Check "GitHub hook trigger for GITScm polling"
6. **Save**: Click "Save"

### Step 2: Set up GitHub Webhook

Since we're using minikube tunnel, we need to use a webhook proxy service:

#### Option A: Using ngrok (Recommended)
1. **Install ngrok**: Download from https://ngrok.com/
2. **Start ngrok**: `ngrok http 8080`
3. **Copy the public URL**: e.g., `https://abc123.ngrok.io`
4. **Add to GitHub**:
   - Go to your GitHub repository
   - Settings → Webhooks → Add webhook
   - Payload URL: `https://abc123.ngrok.io/github-webhook/`
   - Content type: `application/json`
   - Events: "Just the push event"
   - Active: ✅

#### Option B: Using GitHub Actions (Alternative)
Create a GitHub Action that triggers Jenkins via API.

### Step 3: Test the Webhook
1. Make a small change to your code
2. Commit and push to GitHub
3. Check Jenkins - it should automatically start building!

## Option 2: Polling SCM (Simpler)

### Step 1: Configure Jenkins Polling
1. **Access Jenkins**: Go to `http://jenkins.event-booking.local`
2. **Go to your pipeline**: Click on "event-booking-git-pipeline"
3. **Configure**: Click "Configure"
4. **Build Triggers**: Check "Poll SCM"
5. **Schedule**: Enter `H/5 * * * *` (check every 5 minutes)
6. **Save**: Click "Save"

### Step 2: Test Polling
1. Make a change to your code
2. Commit and push to GitHub
3. Wait up to 5 minutes - Jenkins will automatically detect and build!

## Option 3: GitHub Actions (Most Modern)

Create a GitHub Action that builds and deploys directly:

```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Build and Deploy to Minikube
      run: |
        # Your deployment commands here
        echo "Building and deploying..."
```

## Recommended Approach

**For immediate setup**: Use **Option 2 (Polling SCM)** - it's the simplest and works immediately.

**For production**: Use **Option 1 (GitHub Webhook)** with ngrok or a proper webhook proxy.

## Testing Your Automated CI/CD

1. **Make a small change**: Edit any file in your project
2. **Commit and push**:
   ```bash
   git add .
   git commit -m "Test automated CI/CD"
   git push origin main
   ```
3. **Check Jenkins**: Go to `http://jenkins.event-booking.local`
4. **Verify**: You should see a new build automatically started!

## Troubleshooting

### If webhooks don't work:
- Check Jenkins logs: `kubectl logs -n jenkins deployment/jenkins`
- Verify GitHub webhook delivery in repository settings
- Use polling SCM as fallback

### If polling doesn't work:
- Check Jenkins configuration
- Verify Git credentials
- Check Jenkins logs for errors

## Next Steps

Once automated CI/CD is working:
1. Add comprehensive tests
2. Set up notifications (Slack, email)
3. Add security scanning
4. Implement blue-green deployments
5. Add monitoring and alerting

---

**Ready to automate? Choose your preferred option and let's get started!** 🚀
