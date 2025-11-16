# 🔧 Streamlit Cloud Deployment Fix

## Problem: ModuleNotFoundError for Plotly

Error ini terjadi karena dependencies belum terinstall dengan benar di Streamlit Cloud.

## ✅ Quick Fix (3 Steps)

### Step 1: Update requirements.txt

Pastikan file `requirements.txt` di root folder berisi:

```txt
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
```

### Step 2: Force Rebuild

Di Streamlit Cloud:

1. Click "⋮" (three dots) di kanan atas
2. Click "Reboot app"
3. Wait 2-3 minutes

Atau:

1. Push update ke GitHub:
```bash
git add requirements.txt
git commit -m "Fix: Update dependencies"
git push origin main
```

2. Streamlit Cloud akan auto-redeploy

### Step 3: Check Logs

Jika masih error:

1. Click "Manage app" (bottom right)
2. Check logs for specific error
3. Look for `Successfully installed plotly-5.x.x`

## 🔍 Alternative Solutions

### Solution A: Clean Rebuild

```bash
# Delete these files from repo if they exist
rm -rf .streamlit/cache/
rm -rf __pycache__/

# Commit and push
git add .
git commit -m "Clean cache"
git push origin main
```

### Solution B: Minimal Requirements

Create super minimal `requirements.txt`:

```txt
streamlit
plotly
pandas
numpy
```

Then push and let Streamlit Cloud install latest versions.

### Solution C: Pin Specific Versions

```txt
streamlit==1.31.0
plotly==5.18.0
pandas==2.1.4
numpy==1.26.3
```

## 🚀 Verify Installation

After deployment, add this to your app.py (temporary):

```python
import streamlit as st

st.write("Testing imports...")

try:
    import plotly
    st.success(f"✅ Plotly {plotly.__version__}")
except ImportError as e:
    st.error(f"❌ Plotly not found: {e}")

try:
    import pandas
    st.success(f"✅ Pandas {pandas.__version__}")
except ImportError as e:
    st.error(f"❌ Pandas not found: {e}")

try:
    import numpy
    st.success(f"✅ NumPy {numpy.__version__}")
except ImportError as e:
    st.error(f"❌ NumPy not found: {e}")
```

## 📝 Common Streamlit Cloud Issues

### Issue 1: Case Sensitivity

File names are case-sensitive. Make sure:
- `requirements.txt` (lowercase)
- Not `Requirements.txt`
- Not `requirements.TXT`

### Issue 2: File Location

requirements.txt must be in:
- ✅ Root folder (`/requirements.txt`)
- ❌ Not in subfolder

### Issue 3: Encoding

Save requirements.txt as UTF-8:
```bash
file requirements.txt
# Should show: ASCII text or UTF-8 Unicode text
```

### Issue 4: Line Endings

Use Unix line endings (LF), not Windows (CRLF):
```bash
# Fix in VS Code:
# Bottom right: "CRLF" → click → select "LF"

# Or use dos2unix:
dos2unix requirements.txt
```

## 🔄 Step-by-Step Redeploy

If nothing works, completely redeploy:

1. **Delete App** from Streamlit Cloud

2. **Clean Local Repo**:
```bash
git rm -r --cached .
git add .
git commit -m "Clean repo"
```

3. **Create Fresh requirements.txt**:
```bash
echo "streamlit" > requirements.txt
echo "plotly" >> requirements.txt
echo "pandas" >> requirements.txt
echo "numpy" >> requirements.txt
```

4. **Push**:
```bash
git add requirements.txt
git commit -m "Fresh requirements"
git push origin main
```

5. **Deploy New App** on Streamlit Cloud

## 📊 Expected Log Output

When successful, you should see:

```
Collecting streamlit
  Downloading streamlit-1.31.0...
Successfully installed streamlit-1.31.0

Collecting plotly
  Downloading plotly-5.18.0...
Successfully installed plotly-5.18.0

Collecting pandas
  Downloading pandas-2.1.4...
Successfully installed pandas-2.1.4

Collecting numpy
  Downloading numpy-1.26.3...
Successfully installed numpy-1.26.3
```

## 🆘 Still Not Working?

### Option 1: Contact Support

- Email: support@streamlit.io
- Forum: https://discuss.streamlit.io
- Include: App URL, full error logs

### Option 2: Use Local Deployment

```bash
# Run locally instead
pip install -r requirements.txt
streamlit run app.py
```

### Option 3: Alternative Platforms

If Streamlit Cloud continues to fail:
- **Heroku**: Free tier available
- **Railway**: Easy deployment
- **Render**: Streamlit support
- **Fly.io**: Good for Python apps

## ✅ Verification Checklist

Before asking for help, verify:

- [ ] requirements.txt exists in root folder
- [ ] requirements.txt contains all packages
- [ ] File names are lowercase
- [ ] No typos in package names
- [ ] App has been rebooted
- [ ] GitHub repo is up to date
- [ ] Logs show "Successfully installed"
- [ ] No proxy/firewall blocking pip
- [ ] Streamlit Cloud status is operational

## 🎯 Quick Test

Create minimal test app:

**test.py**:
```python
import streamlit as st
import plotly.graph_objects as go

st.title("Plotly Test")

fig = go.Figure(data=[go.Bar(x=[1, 2, 3], y=[4, 5, 6])])
st.plotly_chart(fig)

st.success("Plotly works!")
```

If this works, your requirements.txt is correct!

## 📞 Need Help?

1. **Share error logs** (full text from Streamlit Cloud)
2. **Share requirements.txt** content
3. **Share app.py** (first 20 lines)
4. **Share GitHub repo** (if public)

---

**Most Common Solution**: Just reboot the app! 🔄

90% of the time, a simple reboot fixes the issue.
