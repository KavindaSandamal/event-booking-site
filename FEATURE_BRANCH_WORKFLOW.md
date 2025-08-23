# Feature Branch Workflow Guide

## Overview
This guide explains how to use feature branches to develop new features safely without affecting the main branch.

## Why Feature Branches?
- **Isolation**: Work on features without affecting the main codebase
- **Collaboration**: Multiple developers can work on different features simultaneously
- **Code Review**: Easy to review changes before merging
- **Rollback**: Can easily discard feature work if needed
- **Stable Main**: Main branch stays stable and deployable

## Branch Naming Convention
Use descriptive names with prefixes:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Urgent fixes
- `refactor/` - Code refactoring

Examples:
- `feature/user-authentication`
- `feature/event-booking-system`
- `bugfix/login-validation`
- `hotfix/security-patch`

## Complete Workflow

### 1. Start New Feature
```bash
# Ensure you're on main and it's up to date
git checkout main
git pull origin main

# Create and switch to new feature branch
git checkout -b feature/your-feature-name
```

### 2. Develop Your Feature
```bash
# Make your changes
# Add files
git add .

# Commit with descriptive messages
git commit -m "Add user login functionality"
git commit -m "Implement password validation"
git commit -m "Add remember me checkbox"
```

### 3. Keep Feature Branch Updated
```bash
# While working on feature, periodically sync with main
git checkout main
git pull origin main
git checkout feature/your-feature-name
git merge main
```

### 4. Push Feature Branch
```bash
# Push feature branch to remote
git push -u origin feature/your-feature-name
```

### 5. Create Pull Request
- Go to GitHub repository
- Click "Compare & pull request"
- Add description of your changes
- Request code review from team members

### 6. Merge Feature
```bash
# After PR is approved and merged on GitHub
git checkout main
git pull origin main

# Delete local feature branch
git branch -d feature/your-feature-name

# Delete remote feature branch
git push origin --delete feature/your-feature-name
```

## Best Practices

### Commit Messages
- Use present tense: "Add feature" not "Added feature"
- Be descriptive: "Implement user authentication with JWT tokens"
- Reference issues: "Fix #123: User login validation error"

### Branch Management
- Keep feature branches small and focused
- One feature per branch
- Delete branches after merging
- Never commit directly to main

### Before Merging
- Ensure all tests pass
- Code review completed
- Feature branch is up to date with main
- No merge conflicts

## Example Workflow for Event Booking System

```bash
# 1. Start new feature
git checkout main
git pull origin main
git checkout -b feature/event-booking-system

# 2. Develop feature
# ... make changes ...
git add .
git commit -m "Add event creation form"
git commit -m "Implement date picker component"
git commit -m "Add event validation logic"

# 3. Push feature branch
git push -u origin feature/event-booking-system

# 4. Create PR on GitHub
# 5. After approval and merge
git checkout main
git pull origin main
git branch -d feature/event-booking-system
git push origin --delete feature/event-booking-system
```

## Troubleshooting

### Merge Conflicts
```bash
# If you get merge conflicts
git status  # See conflicted files
# Resolve conflicts manually
git add .
git commit -m "Resolve merge conflicts"
```

### Feature Branch Behind Main
```bash
git checkout feature/your-feature-name
git merge main
# Resolve any conflicts, then continue
```

### Discard Feature Branch
```bash
# If you want to completely discard a feature
git checkout main
git branch -D feature/your-feature-name
git push origin --delete feature/your-feature-name
```

## Current Project Branches
- `main` - Production-ready code
- `feature/user-authentication` - User login/registration system
- `feature/event-booking-system` - Core event booking functionality

## Next Steps
1. Choose which feature to work on first
2. Follow the workflow above
3. Create small, focused commits
4. Push frequently to backup your work
5. Create PRs for code review

Remember: **Never commit directly to main!** Always use feature branches for development.
