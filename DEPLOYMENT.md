# 🚀 Deployment Guide

Complete guide untuk deploy Multi-Chain Arbitrage Bot ke Streamlit Cloud.

## 📋 Prerequisites

- GitHub account
- Git installed di komputer
- Python 3.8+ (untuk testing lokal)

## 🔧 Step-by-Step Deployment

### 1. Setup GitHub Repository

```bash
# Create folder project
mkdir multichain-arbitrage-bot
cd multichain-arbitrage-bot

# Initialize git
git init

# Create semua file yang sudah saya berikan:
# - app.py (main application)
# - requirements.txt
# - README.md
# - LICENSE
# - .gitignore
# - .streamlit/config.toml
```

### 2. Struktur Folder

Pastikan struktur folder seperti ini:

```
multichain-arbitrage-bot/
│
├── .streamlit/
│   └── config.toml
│
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
└── DEPLOYMENT.md (file ini)
```

### 3. Test Locally (Optional)

```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py

# Open browser: http://localhost:8501
```

### 4. Push ke GitHub

```bash
# Add semua files
git add .

# Commit
git commit -m "Initial commit: Multi-chain arbitrage bot"

# Create repository di GitHub.com (via web interface)
# Nama: multichain-arbitrage-bot
# Public atau Private (terserah)

# Link local repo ke GitHub
git remote add origin https://github.com/YOUR_USERNAME/multichain-arbitrage-bot.git

# Push
git branch -M main
git push -u origin main
```

### 5. Deploy ke Streamlit Cloud

1. **Buka** [share.streamlit.io](https://share.streamlit.io)

2. **Sign in** dengan GitHub account

3. **Click** "New app"

4. **Pilih**:
   - Repository: `YOUR_USERNAME/multichain-arbitrage-bot`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL (optional): `your-custom-name` (akan jadi: your-custom-name.streamlit.app)

5. **Click** "Deploy"

6. **Wait** 2-3 menit untuk deployment selesai

7. **Done!** App Anda live di: `https://your-app-name.streamlit.app`

## 🎯 Post-Deployment

### Cek App Status

Setelah deploy, cek:
- ✅ App loads tanpa error
- ✅ All chains menampilkan data
- ✅ Monitoring button works
- ✅ Charts render correctly
- ✅ Trade execution works

### Update App

Untuk update app setelah edit kode:

```bash
# Edit file (misalnya app.py)

# Commit changes
git add .
git commit -m "Update: description of changes"

# Push
git push origin main

# Streamlit Cloud akan auto-redeploy dalam 1-2 menit
```

## 🔒 Security Best Practices

### Jangan Push ke GitHub:

1. **Private Keys**: Jangan pernah commit private keys
2. **API Keys**: Simpan di Streamlit Secrets (jika butuh)
3. **Passwords**: Never hardcode passwords

### Menggunakan Secrets (untuk API keys):

1. Di Streamlit Cloud dashboard, click app Settings
2. Pilih "Secrets"
3. Add secrets dalam format TOML:

```toml
# .streamlit/secrets.toml (JANGAN push ke GitHub)

[api_keys]
alchemy = "your-alchemy-key"
infura = "your-infura-key"
```

4. Access in code:

```python
import streamlit as st

api_key = st.secrets["api_keys"]["alchemy"]
```

## ⚡ Performance Optimization

### Tips untuk Faster App:

1. **Use Caching**:
```python
@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_prices():
    # expensive operation
    return data
```

2. **Limit Rerun Frequency**:
```python
# Tambahkan delay di monitoring loop
time.sleep(5)  # jangan terlalu cepat
```

3. **Lazy Loading**:
```python
# Load data only when needed
if st.button("Load Historical Data"):
    data = load_data()
```

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError"

**Solusi**: Check `requirements.txt`, ensure all dependencies listed

```bash
# Test locally first
pip install -r requirements.txt
streamlit run app.py
```

### Error: "Port already in use"

**Solusi**: Kill existing Streamlit process

```bash
# Mac/Linux
pkill -f streamlit

# Windows
taskkill /f /im streamlit.exe
```

### App is Slow

**Penyebab**:
- Terlalu banyak rerun
- Heavy computations tidak di-cache
- Too many API calls

**Solusi**:
- Add `@st.cache_data` decorator
- Increase rerun interval
- Use session state efficiently

### Deployment Failed

**Check**:
1. GitHub repo is accessible
2. `requirements.txt` exists
3. `app.py` exists in root
4. No syntax errors (test locally)
5. Dependencies are compatible

## 📊 Monitoring App

### Streamlit Cloud Dashboard

Di dashboard Anda bisa lihat:
- **Logs**: Real-time logs dari app
- **Metrics**: CPU, memory usage
- **Errors**: Error traces
- **Analytics**: Viewer count, page views

### Access Logs

```bash
# Logs available in Streamlit Cloud dashboard
# Or via CLI (if configured)
streamlit logs
```

## 🔄 Auto-Redeployment

Streamlit Cloud automatically redeploys when:
- You push changes to GitHub
- You update secrets
- You change app settings

Typical redeploy time: 1-3 minutes

## 💡 Advanced: Custom Domain

1. **Upgrade** to Streamlit for Teams (paid)
2. **Configure** custom domain in settings
3. **Update** DNS records:
   - Type: CNAME
   - Name: your-subdomain
   - Value: your-app.streamlit.app

## 📱 Mobile Optimization

App sudah responsive, tapi untuk better UX:

```python
# Detect mobile
if st.sidebar.button("Mobile View"):
    st.session_state.mobile_view = True

# Adjust layout
if st.session_state.get('mobile_view'):
    st.write("Mobile-optimized content")
```

## 🎨 Customization

### Change Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor="#your-color"
backgroundColor="#your-bg"
secondaryBackgroundColor="#your-secondary-bg"
textColor="#your-text-color"
font="sans serif"  # or "serif" or "monospace"
```

### Add Logo

```python
st.sidebar.image("logo.png", use_column_width=True)
```

## 📈 Analytics

### Add Google Analytics

```python
# In app.py
st.markdown("""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
""", unsafe_allow_html=True)
```

## 🔗 Useful Links

- **Streamlit Docs**: https://docs.streamlit.io
- **Streamlit Cloud**: https://share.streamlit.io
- **Community Forum**: https://discuss.streamlit.io
- **GitHub**: https://github.com/streamlit/streamlit

## 📞 Support

Jika ada masalah:

1. **Check Logs** di Streamlit Cloud dashboard
2. **Test Locally** dengan `streamlit run app.py`
3. **Search** Streamlit forum
4. **Create Issue** di GitHub repository Anda

## ✅ Deployment Checklist

Before deploying, make sure:

- [ ] All files created and in correct structure
- [ ] `requirements.txt` has all dependencies
- [ ] Tested locally and works
- [ ] No sensitive data in code
- [ ] README.md updated with your info
- [ ] Git repository initialized
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud account created
- [ ] App deployed successfully
- [ ] App URL works and is accessible
- [ ] Shared app link with others

## 🎉 Success!

Your app is now live! Share the URL:
`https://your-app-name.streamlit.app`

---

**Happy Deploying! 🚀**
