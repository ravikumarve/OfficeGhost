# GhostOffice Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install GhostOffice

**Linux:**
```bash
# Download and run the installer
chmod +x install.sh
./install.sh
```

**macOS:**
```bash
# Download and run the installer
chmod +x install.sh
./install.sh
```

### Step 2: Start GhostOffice

```bash
# Activate the virtual environment
source venv/bin/activate

# Start GhostOffice
python3 main.py
```

### Step 3: Access the Dashboard

Open your browser and go to: **http://localhost:5000**

### Step 4: Complete Setup Wizard

1. **Create your master password** (minimum 12 characters)
2. **Configure your email accounts** (optional)
3. **Select your watch folders** (optional)
4. **Choose your AI model** (phi3:mini is recommended)

### Step 5: Start Using GhostOffice

Once setup is complete, you can:

- **📧 Scan Emails**: Automatically classify and draft replies
- **📁 Sort Files**: Organize documents into smart categories
- **📊 Extract Data**: Parse invoices and receipts
- **🧠 Learn**: GhostOffice learns from your corrections

---

## 🎯 Demo Mode

Want to see GhostOffice in action without setting up email accounts?

1. Open `.env` file in a text editor
2. Change `DEMO_MODE=false` to `DEMO_MODE=true`
3. Restart GhostOffice
4. Access the dashboard with pre-populated sample data

---

## 🔐 Security Features

- **AES-256 Encryption**: All your data is encrypted
- **100% Local**: Nothing is sent to the cloud
- **Biometric Unlock**: Use Windows Hello, Touch ID, or Linux PAM
- **2FA Support**: Add an extra layer of security

---

## 📧 Email Setup (Optional)

GhostOffice works with any email provider that supports IMAP/SMTP:

- Gmail
- Outlook
- ProtonMail
- Yahoo Mail
- And many more...

To set up email:

1. Go to Settings in the dashboard
2. Click "Add Email Account"
3. Enter your email credentials
4. Test the connection
5. Save and start scanning

---

## 📁 File Watching (Optional)

GhostOffice can automatically organize your files:

1. Go to Settings in the dashboard
2. Add watch folders (e.g., Downloads, Desktop)
3. GhostOffice will automatically sort new files

---

## 🧠 AI Models

GhostOffice uses Ollama for local AI processing:

**Recommended Models:**
- **phi3:mini** (default) - Fast and lightweight
- **llama3.2:3b** - Good balance of speed and accuracy
- **llama3.2** - Best accuracy (requires more RAM)

To change models:

1. Go to Settings in the dashboard
2. Select your preferred model
3. Click "Pull Model" to download

---

## 🛠️ Troubleshooting

### GhostOffice won't start

**Check if Ollama is running:**
```bash
ollama list
```

**Start Ollama if needed:**
```bash
ollama serve
```

### Can't access the dashboard

**Check if the port is in use:**
```bash
# Linux
netstat -tlnp | grep 5000

# macOS
lsof -i :5000
```

**Change the port in .env:**
```
DASHBOARD_PORT=5001
```

### Email connection fails

1. Check your email credentials
2. Enable IMAP in your email settings
3. Use an app-specific password if required (Gmail)
4. Check your firewall settings

---

## 📚 Need More Help?

- **Documentation**: See README.md for detailed information
- **Architecture**: See ARCHITECTURE.md for system design
- **API Reference**: See docs/API.md for API documentation

---

## 🎉 You're All Set!

GhostOffice is now running and ready to help you:

- ✅ Automatically classify emails
- ✅ Draft smart replies
- ✅ Organize your files
- ✅ Extract data from documents
- ✅ Learn your preferences

**Remember**: GhostOffice runs 100% locally. Your data never leaves your machine.

---

## 🔄 Updates

To update GhostOffice:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Restart GhostOffice
python3 main.py
```

---

## 📞 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Review the logs in `data/logs/`
3. Check the GitHub issues page

---

**👻 Welcome to GhostOffice - Your Private AI Assistant!**
