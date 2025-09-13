#!/usr/bin/env python3
"""
TopStyle Business Deployment Script
Automates the deployment process for various platforms
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check if git is installed
    if not run_command("git --version", "Checking Git"):
        print("❌ Git is not installed. Please install Git first.")
        return False
    
    # Check if Python is installed
    if not run_command("python --version", "Checking Python"):
        print("❌ Python is not installed. Please install Python first.")
        return False
    
    print("✅ All requirements met!")
    return True

def prepare_deployment():
    """Prepare the project for deployment"""
    print("🚀 Preparing project for deployment...")
    
    # Create .gitignore if it doesn't exist
    gitignore_content = """# Django
*.log
*.pot
*.pyc
__pycache__/
local_settings.py
db.sqlite3
db.sqlite3-journal
media/

# Environment variables
.env
.venv
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Deployment
staticfiles/
"""
    
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore file")
    
    # Create production environment file
    env_content = """SECRET_KEY=your-super-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=your-domain.com,*.railway.app,*.onrender.com,*.herokuapp.com
DATABASE_URL=sqlite:///db.sqlite3
"""
    
    if not os.path.exists('.env.production'):
        with open('.env.production', 'w') as f:
            f.write(env_content)
        print("✅ Created production environment template")
    
    return True

def initialize_git():
    """Initialize git repository and make initial commit"""
    print("📦 Initializing Git repository...")
    
    # Check if git is already initialized
    if os.path.exists('.git'):
        print("✅ Git repository already exists")
        return True
    
    # Initialize git
    if not run_command("git init", "Initializing Git repository"):
        return False
    
    # Add all files
    if not run_command("git add .", "Adding files to Git"):
        return False
    
    # Make initial commit
    if not run_command('git commit -m "Initial commit - TopStyle Business App"', "Making initial commit"):
        return False
    
    return True

def show_deployment_options():
    """Show deployment platform options"""
    print("\n" + "="*60)
    print("🌟 DEPLOYMENT OPTIONS")
    print("="*60)
    
    print("\n1. 🚂 RAILWAY (Recommended - Easiest)")
    print("   • Go to: https://railway.app")
    print("   • Sign up with GitHub")
    print("   • Click 'New Project' → 'Deploy from GitHub repo'")
    print("   • Select your repository")
    print("   • Railway automatically deploys!")
    
    print("\n2. 🎨 RENDER (Popular Choice)")
    print("   • Go to: https://render.com")
    print("   • Sign up with GitHub")
    print("   • Click 'New +' → 'Web Service'")
    print("   • Connect your repository")
    print("   • Configure build settings and deploy")
    
    print("\n3. 🟣 HEROKU (Classic Choice)")
    print("   • Go to: https://heroku.com")
    print("   • Install Heroku CLI")
    print("   • Run: heroku create your-app-name")
    print("   • Run: git push heroku main")
    
    print("\n4. ⚡ VERCEL (Fast Deployment)")
    print("   • Go to: https://vercel.com")
    print("   • Import your GitHub repository")
    print("   • Configure Django settings")
    print("   • Deploy with one click")
    
    print("\n" + "="*60)

def create_github_repo_instructions():
    """Show GitHub repository creation instructions"""
    print("\n📋 GITHUB REPOSITORY SETUP")
    print("="*40)
    
    print("\n1. Go to: https://github.com")
    print("2. Sign up or log in")
    print("3. Click 'New repository'")
    print("4. Repository name: topstyle-business-app")
    print("5. Make it Public (required for free hosting)")
    print("6. Click 'Create repository'")
    print("7. Copy the repository URL")
    print("8. Run these commands:")
    print("   git remote add origin https://github.com/YOUR_USERNAME/topstyle-business-app.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    
    print("\n" + "="*40)

def main():
    """Main deployment script"""
    print("🚀 TopStyle Business Deployment Script")
    print("="*50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please install missing tools.")
        return
    
    # Prepare deployment
    if not prepare_deployment():
        print("\n❌ Deployment preparation failed.")
        return
    
    # Initialize git
    if not initialize_git():
        print("\n❌ Git initialization failed.")
        return
    
    # Show deployment options
    show_deployment_options()
    
    # Show GitHub setup instructions
    create_github_repo_instructions()
    
    print("\n🎉 DEPLOYMENT PREPARATION COMPLETE!")
    print("="*50)
    print("\nNext steps:")
    print("1. Create a GitHub repository")
    print("2. Push your code to GitHub")
    print("3. Choose a hosting platform")
    print("4. Deploy your app!")
    print("5. Get your live URL and share it!")
    
    print("\n📱 After deployment:")
    print("• Your app will be accessible from anywhere")
    print("• Mobile users can install it as an app")
    print("• Automatic HTTPS and security")
    print("• Professional domain name")
    
    print("\n🔗 Your app will be live at:")
    print("• Railway: https://your-app.railway.app")
    print("• Render: https://your-app.onrender.com")
    print("• Heroku: https://your-app.herokuapp.com")
    print("• Vercel: https://your-app.vercel.app")
    
    print("\n✨ Happy deploying!")

if __name__ == "__main__":
    main()
