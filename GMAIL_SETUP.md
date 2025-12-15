# Gmail Setup for Password Reset

This guide explains how to configure Gmail to send password reset verification codes.

## Step 1: Enable 2-Factor Authentication

1. Go to your Google Account settings: https://myaccount.google.com/
2. Navigate to **Security**
3. Under **Signing in to Google**, enable **2-Step Verification**

## Step 2: Generate an App Password

1. Go to your Google Account settings: https://myaccount.google.com/
2. Navigate to **Security**
3. Under **Signing in to Google**, click on **App passwords**
4. Select **Mail** as the app and **Other (Custom name)** as the device
5. Enter "TopStyle Business" as the custom name
6. Click **Generate**
7. Copy the 16-character password (it will look like: `abcd efgh ijkl mnop`)

## Step 3: Configure Environment Variables

1. Create or update your `.env` file in the project root
2. Add the following variables:

```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Important Notes:**
- Use your Gmail address for `EMAIL_HOST_USER` and `DEFAULT_FROM_EMAIL`
- Use the 16-character app password (without spaces) for `EMAIL_HOST_PASSWORD`
- Never commit your `.env` file to version control

## Step 4: Test Email Configuration

Before using the password reset feature, test your email configuration:

### Option 1: Using the Test Script (Recommended)
```bash
python test_email_config.py
```
This will:
- Check your email configuration
- Prompt you for a recipient email
- Send a test email with a verification code
- Show detailed error messages if something fails

### Option 2: Using Django Management Command
```bash
python manage.py test_email your-email@gmail.com
```
This will send a test email to the specified address.

### Option 3: Test via Password Reset
1. Make sure your Django settings are configured correctly (already done in `settings.py`)
2. Test the password reset functionality by:
   - Going to the login page
   - Clicking "Forgot Password?"
   - Entering a valid username and email
   - Checking your email for the verification code (including spam folder)

## Troubleshooting

### Email not sending?
- Verify that 2-Factor Authentication is enabled
- Check that you're using the App Password (not your regular Gmail password)
- Ensure the app password doesn't have spaces
- Check that your `.env` file is in the project root
- Verify that the email settings in `settings.py` are correct

### "Invalid credentials" error?
- Make sure you're using the App Password, not your regular Gmail password
- Verify that 2-Factor Authentication is enabled on your Google account
- Check that the app password hasn't been revoked

### Email going to spam?
- The email is sent from your Gmail address
- Check your spam folder
- Add the sending address to your contacts if needed

## Security Notes

- App passwords are more secure than using your regular Gmail password
- App passwords can be revoked individually without affecting your main account
- Never share your app password
- Rotate app passwords periodically for better security

