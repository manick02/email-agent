
Never commit credentials.json and token.json to source repository. Below is the notest from deepseek to generate credentials.json


Step-by-Step Instructions to Get credentials.json
1. Go to Google Cloud Console
Navigate to: Google Cloud Console

Sign in with your Google account (use the account that owns the Gmail you want to access)

2. Create or Select a Project
Click the project dropdown (top-left) → "NEW PROJECT"

Name: Gmail API Project (or any name)

Click "CREATE"

3. Enable the Gmail API
In the left sidebar, go to:
APIs & Services → Library

Search for "Gmail API" → Click on it → "ENABLE"

4. Configure OAuth Consent Screen
Go to: APIs & Services → OAuth consent screen

Select User Type:

For personal use: Choose "External" → Click "CREATE"

Fill in required fields:

App name: Gmail Poller (or any name)

User support email: Select your email

Developer contact email: Add your email

Click "SAVE AND CONTINUE" (skip optional scopes for now)

5. Create OAuth Credentials
Go to: APIs & Services → Credentials

Click "+ CREATE CREDENTIALS" → "OAuth client ID"

Select application type: "Desktop app"

Name: Gmail Poller Client (or any name)

Click "CREATE"

6. Download credentials.json
After creation, click the download icon (⤓) next to your OAuth client

Save the file as credentials.json in your project folder