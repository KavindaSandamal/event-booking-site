# GitHub Webhook Setup for Jenkins CI/CD

## 🔗 **GitHub Webhook Configuration**

### **Step 1: Access Your GitHub Repository**
1. Go to your GitHub repository: `https://github.com/yourusername/event-booking-platform`
2. Click on **Settings** tab
3. Click on **Webhooks** in the left sidebar
4. Click **Add webhook**

### **Step 2: Configure Webhook**
- **Payload URL**: `http://jenkins.event-booking.local/jenkins/github-webhook/`
- **Content type**: `application/json`
- **Secret**: (Leave empty for now, or create a secret for security)
- **SSL verification**: Disable (for local development)

### **Step 3: Select Events**
Choose **Let me select individual events** and select:
- ✅ **Push** - Triggers on code pushes
- ✅ **Pull request** - Triggers on PR creation/updates
- ✅ **Issues** - Triggers on issue creation/updates
- ✅ **Release** - Triggers on new releases

### **Step 4: Save Webhook**
Click **Add webhook** to save the configuration.

## 🌐 **Public URL Setup (for GitHub to reach your local Jenkins)**

Since GitHub needs to reach your local Jenkins, you have several options:

### **Option 1: ngrok (Recommended for Development)**
```bash
# Install ngrok
# Download from https://ngrok.com/download

# Start ngrok tunnel
ngrok http 80

# Use the ngrok URL in your webhook
# Example: https://abc123.ngrok.io/jenkins/github-webhook/
```

### **Option 2: Cloudflare Tunnel**
```bash
# Install cloudflared
# Download from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# Start tunnel
cloudflared tunnel --url http://localhost:80
```

### **Option 3: LocalTunnel**
```bash
# Install localtunnel
npm install -g localtunnel

# Start tunnel
lt --port 80

# Use the provided URL in your webhook
```

## 🔧 **Jenkins Configuration**

### **Step 1: Install Required Plugins**
In Jenkins, go to **Manage Jenkins** > **Manage Plugins** and install:
- ✅ **GitHub Integration**
- ✅ **GitHub API**
- ✅ **GitHub Branch Source**
- ✅ **Pipeline: GitHub**
- ✅ **GitHub Authentication**

### **Step 2: Configure GitHub Credentials**
1. Go to **Manage Jenkins** > **Manage Credentials**
2. Click **System** > **Global credentials** > **Add Credentials**
3. Choose **GitHub App** or **Username with password**
4. Add your GitHub credentials

### **Step 3: Configure GitHub Server**
1. Go to **Manage Jenkins** > **Configure System**
2. Find **GitHub** section
3. Add GitHub Server:
   - **Name**: `GitHub`
   - **API URL**: `https://api.github.com`
   - **Credentials**: Select your GitHub credentials
   - **Manage hooks**: ✅ Check this box

### **Step 4: Create Jenkins Job**
1. Click **New Item**
2. Enter job name: `event-booking-platform`
3. Choose **Pipeline**
4. Click **OK**

### **Step 5: Configure Pipeline**
1. In the job configuration:
   - **Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: `https://github.com/yourusername/event-booking-platform.git`
   - **Credentials**: Select your GitHub credentials
   - **Branch Specifier**: `*/main`
   - **Script Path**: `jenkins/Jenkinsfile`

### **Step 6: Configure Triggers**
1. In **Build Triggers** section:
   - ✅ **GitHub hook trigger for GITScm polling**
   - ✅ **Poll SCM** (optional, as backup)
   - **Schedule**: `H/5 * * * *` (every 5 minutes)

## 🧪 **Testing the Webhook**

### **Test 1: Manual Trigger**
1. Make a small change to your code
2. Commit and push to GitHub
3. Check Jenkins dashboard for new build

### **Test 2: Webhook Delivery**
1. Go to your GitHub repository > Settings > Webhooks
2. Click on your webhook
3. Scroll down to **Recent Deliveries**
4. Click on a delivery to see details

### **Test 3: Jenkins Logs**
1. In Jenkins, go to your job
2. Click on a build
3. Check **Console Output** for webhook details

## 🔍 **Troubleshooting**

### **Common Issues:**

#### **1. Webhook Not Triggering**
- Check webhook URL is correct
- Verify Jenkins is accessible from internet
- Check GitHub webhook delivery logs
- Ensure Jenkins job has correct triggers enabled

#### **2. Authentication Issues**
- Verify GitHub credentials in Jenkins
- Check GitHub App permissions
- Ensure repository access is granted

#### **3. Pipeline Not Starting**
- Check Jenkinsfile syntax
- Verify SCM configuration
- Check branch specifier matches your branch

#### **4. Build Failures**
- Check console output for errors
- Verify Docker and kubectl are available
- Check Minikube is running

### **Debug Commands:**
```bash
# Check Jenkins logs
docker-compose logs -f jenkins

# Check webhook endpoint
curl -X POST http://jenkins.event-booking.local/jenkins/github-webhook/ \
  -H "Content-Type: application/json" \
  -d '{"ref":"refs/heads/main","repository":{"name":"event-booking-platform"}}'

# Check GitHub webhook delivery
# Go to GitHub repo > Settings > Webhooks > Click webhook > Recent Deliveries
```

## 📋 **Webhook Payload Example**

GitHub sends a payload like this:
```json
{
  "ref": "refs/heads/main",
  "before": "a1b2c3d4e5f6",
  "after": "f6e5d4c3b2a1",
  "repository": {
    "name": "event-booking-platform",
    "full_name": "yourusername/event-booking-platform"
  },
  "pusher": {
    "name": "yourusername",
    "email": "your@email.com"
  },
  "commits": [
    {
      "id": "f6e5d4c3b2a1",
      "message": "Update CI/CD pipeline",
      "author": {
        "name": "Your Name",
        "email": "your@email.com"
      }
    }
  ]
}
```

## 🎯 **Success Indicators**

✅ **Webhook is working when:**
- GitHub shows successful webhook deliveries
- Jenkins automatically starts builds on code pushes
- Build logs show webhook trigger information
- Pipeline stages execute successfully

## 🚀 **Next Steps**

1. **Set up branch protection rules** in GitHub
2. **Configure automatic deployment** to staging/production
3. **Add Slack/email notifications** for build results
4. **Set up SonarQube quality gates**
5. **Configure automated testing** and coverage reports

---

**Need Help?** Check the Jenkins and GitHub documentation for more detailed information.
