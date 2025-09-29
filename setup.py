#!/usr/bin/env python3
"""
Setup script for Brevo Webhook Handler
This script helps you configure your environment variables
"""
import os
import sys

def create_env_file():
    """Create .env file with user input"""
    print("🔧 Setting up Brevo Webhook Handler")
    print("=" * 40)
    
    # Get port
    port = input("Enter port number (default: 3000): ").strip()
    if not port:
        port = "3000"
    
    # Get webhook secret
    webhook_secret = input("Enter your Brevo webhook secret: ").strip()
    if not webhook_secret:
        print("❌ Webhook secret is required!")
        return False
    
    # Create .env content
    env_content = f"""PORT={port}
BREVO_WEBHOOK_SECRET={webhook_secret}
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def show_manual_setup():
    """Show manual setup instructions"""
    print("\n📋 Manual Setup Instructions:")
    print("=" * 40)
    print("1. Create a file named '.env' in your project root")
    print("2. Add the following content:")
    print("   PORT=3000")
    print("   BREVO_WEBHOOK_SECRET=your_actual_webhook_secret")
    print("\n3. Replace 'your_actual_webhook_secret' with your real Brevo webhook secret")
    print("\n4. Save the file and run: python main.py")

def main():
    """Main setup function"""
    print("🚀 Brevo Webhook Handler Setup")
    print("=" * 40)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️ .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Try to create .env file
    if create_env_file():
        print("\n🎉 Setup complete!")
        print("You can now run: python main.py")
    else:
        print("\n📝 Manual setup required:")
        show_manual_setup()

if __name__ == "__main__":
    main()
