# Deploy to Railway - Step by Step

## Prerequisites

✅ Code pushed to GitHub  
✅ Hugging Face API token (get from https://huggingface.co/settings/tokens)

---

## Step 1: Create Railway Account

1. Go to: **https://railway.app**
2. Click **"Start a New Project"**
3. Sign up with **GitHub** (recommended - one click)
4. Authorize Railway to access your GitHub repositories

---

## Step 2: Deploy from GitHub

1. In Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select your repository: **`rag-kb-bot`**
4. Railway will automatically:
   - Detect the Dockerfile
   - Start building your app
   - Begin deployment

**⏳ Wait 2-3 minutes for the first build**

---

## Step 3: Add Environment Variables

1. Click on your deployed service (the card that appears)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add this variable:

   **Name:** `HF_API_KEY`  
   **Value:** `your_huggingface_token_here`  
   (Paste the token you got from Hugging Face)

5. Click **"Add"**

**Optional (can skip):**
- `HF_API_URL` - Only if you want a different model
- `LLM_PROVIDER` - Already set to `huggingface` by default

---

## Step 4: Add Persistent Storage (for ChromaDB)

1. In your service, go to **"Settings"** tab
2. Scroll down to **"Volumes"** section
3. Click **"+ Add Volume"**
4. Configure:
   - **Mount Path:** `/app/chroma_db`
   - **Size:** 1 GB (free tier limit)
5. Click **"Add Volume"**

**Why?** This stores your indexed documents permanently.

---

## Step 5: Get Your Public URL

1. Go to **"Settings"** tab
2. Scroll to **"Domains"** section
3. Railway automatically creates a domain like:
   - `rag-kb-bot-production.up.railway.app`
4. If no domain exists, click **"Generate Domain"**
5. **Copy your URL!** This is your live app.

---

## Step 6: Test Your Deployment

1. Open your Railway URL in a browser
2. You should see the RAG Knowledge Base Assistant interface
3. Upload a test document (PDF, TXT, or MD)
4. Wait for indexing (few seconds)
5. Ask a question about the document
6. **First query may take 20-30 seconds** (model loading - normal!)
7. Subsequent queries are faster

**✅ Your app is live!**

---

## Troubleshooting

### Build Fails
- Check Railway logs (click "View Logs" button)
- Make sure all files are committed to GitHub
- Verify Dockerfile is in root directory

### App Crashes
- Check Railway logs
- Verify `HF_API_KEY` environment variable is set
- Check if Hugging Face API is accessible

### Slow First Response
- **Normal!** Free tier models "sleep" when not used
- First request wakes up the model (20-30 seconds)
- Subsequent requests are much faster

### "Model is loading" Error
- Wait 20-30 seconds
- Try again
- Free tier models need time to wake up

---

## Monitoring

- **Logs:** Click "View Logs" to see real-time application logs
- **Metrics:** See CPU, memory, network usage
- **Deployments:** View build history

---

## Updating Your App

1. Push changes to GitHub
2. Railway automatically detects changes
3. Triggers new deployment
4. Updates live in 2-3 minutes

**No manual steps needed!**

---

## Cost

**Free Tier:**
- $5 free credit per month
- 512MB RAM
- 1GB storage
- 100GB bandwidth

**This app uses:**
- ~200MB RAM
- ~100MB storage
- Minimal bandwidth

**Total: $0/month!** 🎉

---

## That's It!

Your RAG Knowledge Base is now live and publicly accessible!

**Need help?** Check Railway logs or the troubleshooting section above.
