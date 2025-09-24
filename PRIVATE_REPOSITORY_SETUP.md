# 🔒 Private Knowledge Repository Setup

## 🎯 Overview

This setup creates a **separate private GitHub repository** for your knowledge library while keeping the bot code public. Perfect for sharing the bot while keeping your personal learning private!

## 📁 Repository Structure

```
📂 Your Setup:
├── 🤖 Knowledge-Bot/ (PUBLIC - this repository)
│   ├── bot/
│   ├── services/ 
│   ├── storage/
│   └── config.py
│
└── 🔒 my-private-knowledge/ (PRIVATE - your knowledge)
    ├── 📑 00_Index/
    ├── 🤖 01_Artificial_Intelligence/
    ├── 💰 02_Making_Money_with_AI/
    ├── 💻 03_Computer_Science/
    ├── 🍎 04_Mac_and_Apple/
    ├── 🐧 05_Linux_and_DevOps/
    ├── 📈 06_Productivity_and_Tools/
    └── .obsidian/ (Obsidian configuration)
```

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Private Repository on GitHub
1. Go to [GitHub](https://github.com/new)
2. Repository name: `my-private-knowledge`
3. ✅ **Make it Private**
4. ✅ Initialize with README
5. Click "Create repository"

### Step 2: Generate GitHub Personal Access Token
1. Go to [GitHub Settings → Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Name: `Knowledge Bot Access`
4. Expiration: `No expiration` (or 1 year)
5. Scopes: ✅ **repo** (full control of private repositories)
6. Click "Generate token"
7. **Copy the token** (you won't see it again!)

### Step 3: Run Setup Script
```bash
cd /Users/silvio/Documents/GitHub/Knowledge-Bot
python3 setup_private_repo.py
```

The script will ask for:
- Your GitHub username
- Your GitHub Personal Access Token

### Step 4: Update Your .env File
Copy the generated settings from `private_repo.env` to your main `.env` file:

```bash
# Add these to your .env file:
STORAGE_MODE=book
OBSIDIAN_VAULT_PATH=../my-private-knowledge
PRIVATE_REPO_PATH=../my-private-knowledge
GITHUB_USERNAME=your_username
GITHUB_TOKEN=your_token
AUTO_COMMIT=true
AUTO_PUSH=true
```

## ✨ Features

### 🔄 **Automatic Git Sync**
- Every new knowledge entry is automatically committed
- Pushes to your private GitHub repository  
- Professional commit messages
- Full version history

### 🔒 **Privacy Control**
- Your knowledge stays in a separate private repo
- Bot code remains public for sharing
- No sensitive data in public repository

### 📱 **Mobile Access**
- Obsidian mobile app syncs with your private repo
- Read your knowledge library anywhere
- Always up to date

### 📊 **Professional Organization**
- Git history tracks your learning progress
- Structured commits with meaningful messages
- Easy to backup and restore

## 🎯 How It Works

### When You Send a Video URL:

1. **Bot processes** → Downloads and analyzes video
2. **You approve** → Content gets enriched 
3. **Auto-saved** → Creates beautiful book page in `../my-private-knowledge/`
4. **Auto-committed** → Git commit: "Add: Video Title"
5. **Auto-pushed** → Syncs to your private GitHub repo
6. **Obsidian syncs** → Available on all your devices

### Repository Structure Created:

```bash
my-private-knowledge/
├── README.md (private repository info)
├── 00_Index/Home.md (library homepage)
├── 01_Artificial_Intelligence/
│   ├── 01_Artificial_Intelligence.md (section index)
│   └── 001_Your_First_AI_Video.md (content pages)
├── 02_Making_Money_with_AI/
├── 03_Computer_Science/
├── 04_Mac_and_Apple/
├── 05_Linux_and_DevOps/
├── 06_Productivity_and_Tools/
└── .obsidian/ (beautiful book theme + settings)
```

## 📱 Obsidian Setup

### Install Obsidian:
1. Download from [obsidian.md](https://obsidian.md) (FREE!)
2. Open Obsidian
3. Choose "Open folder as vault"
4. Select: `../my-private-knowledge`

### Enable Features:
1. **Settings** → **Appearance** → **CSS snippets** → Enable `knowledge-library-book-theme`
2. **Community plugins** → Install **Dataview** → Enable
3. Navigate to `00_Index/Home.md` for your library homepage

## 🔧 Commands & Management

### Check Repository Status:
```python
from services.git_sync import GitKnowledgeSync
git_sync = GitKnowledgeSync()
status = await git_sync.get_status()
print(status)
```

### Manual Commit:
```python  
from services.git_sync import auto_sync_knowledge
await auto_sync_knowledge("path/to/file.md", "Manual Entry Title")
```

### Repository Information:
- **Location**: `../my-private-knowledge`
- **GitHub URL**: `https://github.com/YOUR_USERNAME/my-private-knowledge`
- **Obsidian Vault**: Same directory

## 🔒 Security Features

### ✅ **What's Private:**
- All your knowledge content
- Personal learning notes
- Video sources and metadata
- Reading history and progress

### ✅ **What's Public:**
- Bot source code (this repository)
- Installation instructions
- Feature documentation

### ✅ **Token Security:**
- Token stored in `.env` (gitignored)
- Full repo access for seamless sync
- Revokable anytime from GitHub settings

## 🎯 Benefits

### **📚 For You:**
- Private, organized knowledge library
- Beautiful reading experience
- Cross-device synchronization
- Version-controlled learning history

### **🌍 For Others:**
- Can use your bot code
- Can follow your setup guide
- Can adapt for their own use
- Your knowledge stays private

## 🚀 Getting Started

1. **Run the setup script**: `python3 setup_private_repo.py`
2. **Update your .env file** with the generated settings
3. **Install Obsidian** and open your vault
4. **Start your bot** and send a video URL!

Your private knowledge library will be automatically created, organized, and synced! 🎉

## 📞 Need Help?

- **Setup Issues**: Check GitHub token permissions
- **Sync Problems**: Verify repository exists and is accessible
- **Obsidian Questions**: Enable Dataview plugin for dynamic features
- **Git Errors**: Ensure repository path is correct

---

**🔒 Your knowledge is private, your code is public, everyone wins!** 🚀