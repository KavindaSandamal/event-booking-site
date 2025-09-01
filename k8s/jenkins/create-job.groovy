// Create Jenkins job for event-booking platform
import jenkins.model.*
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import hudson.plugins.git.*

def instance = Jenkins.getInstance()

// Create the job
def job = new WorkflowJob(instance, "event-booking-cicd")
job.setDescription("CI/CD Pipeline for Event Booking Platform")

// Configure Git SCM
def gitScm = new GitSCM("https://github.com/your-username/event-booking-platform.git")
gitScm.setBranches([new BranchSpec("*/main")])

// Configure pipeline definition
def flowDefinition = new CpsScmFlowDefinition(gitScm, "Jenkinsfile")
job.setDefinition(flowDefinition)

// Configure build triggers
def triggers = []
triggers.add(new hudson.triggers.SCMTrigger("H/5 * * * *")) // Poll every 5 minutes
job.setTriggers(triggers)

// Save the job
job.save()

println "Jenkins job 'event-booking-cicd' created successfully!"
