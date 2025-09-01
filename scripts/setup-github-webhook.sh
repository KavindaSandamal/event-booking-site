#!/bin/bash

# GitHub Webhook Setup Script for Jenkins CI/CD
echo "🔗 Setting up GitHub webhook for Jenkins CI/CD..."

# Configuration
JENKINS_URL="http://localhost:8080"
GITHUB_REPO="your-username/event-booking-platform"
GITHUB_TOKEN="your-github-token"

echo "📋 Webhook Configuration:"
echo "   Jenkins URL: $JENKINS_URL"
echo "   GitHub Repo: $GITHUB_REPO"
echo ""

# Create webhook payload
WEBHOOK_PAYLOAD=$(cat <<EOF
{
  "name": "web",
  "active": true,
  "events": [
    "push",
    "pull_request"
  ],
  "config": {
    "url": "$JENKINS_URL/github-webhook/",
    "content_type": "json",
    "insecure_ssl": "0"
  }
}
EOF
)

echo "🔧 To set up the webhook manually:"
echo ""
echo "1. Go to your GitHub repository: https://github.com/$GITHUB_REPO"
echo "2. Navigate to: Settings → Webhooks → Add webhook"
echo "3. Configure:"
echo "   - Payload URL: $JENKINS_URL/github-webhook/"
echo "   - Content type: application/json"
echo "   - Events: Push, Pull requests"
echo "   - Active: ✓"
echo ""
echo "4. Click 'Add webhook'"
echo ""

# Alternative: Use GitHub API (requires token)
if [ "$GITHUB_TOKEN" != "your-github-token" ]; then
    echo "🚀 Creating webhook via GitHub API..."
    
    curl -X POST \
      -H "Authorization: token $GITHUB_TOKEN" \
      -H "Accept: application/vnd.github.v3+json" \
      -d "$WEBHOOK_PAYLOAD" \
      "https://api.github.com/repos/$GITHUB_REPO/hooks"
    
    echo "✅ Webhook created successfully!"
else
    echo "⚠️  Set GITHUB_TOKEN environment variable to create webhook automatically"
fi

echo ""
echo "📚 Additional Configuration:"
echo ""
echo "1. In Jenkins, install GitHub Plugin:"
echo "   - Manage Jenkins → Manage Plugins → Available"
echo "   - Search for 'GitHub Integration'"
echo "   - Install and restart Jenkins"
echo ""
echo "2. Configure GitHub in Jenkins:"
echo "   - Manage Jenkins → Configure System"
echo "   - GitHub section → Add GitHub Server"
echo "   - API URL: https://api.github.com"
echo "   - Add credentials (GitHub token)"
echo ""
echo "3. Enable webhook trigger in your job:"
echo "   - Job configuration → Build Triggers"
echo "   - Check 'GitHub hook trigger for GITScm polling'"
echo ""
echo "✅ Webhook setup instructions completed!"
