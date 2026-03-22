# Azure Configuration Guide for Phoenix

Step-by-step instructions to set up the Azure services required by Phoenix.

---

## 1. Azure AI Foundry — Deploy LLM Models

### Step 1: Create an Azure AI Hub + Project

1. Go to [Azure Portal](https://portal.azure.com) → search **"Azure AI Foundry"**
2. Click **"+ Create"** → select **"Hub"**
3. Fill in:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Create new or use existing (e.g., `phoenix-rg`)
   - **Region**: `East US` (or your preferred region)
   - **Hub name**: `phoenix-ai-hub`
4. Click **Review + Create** → **Create**
5. Once deployed, go to the hub → click **"+ New project"** → name it `phoenix-project`

### Step 2: Deploy Models

For each model you want to use (GPT-4o, Claude 3.5 Sonnet, Mistral Large):

1. In the Azure AI Foundry portal → go to your project
2. Click **"Model catalog"** in the left sidebar
3. Search for the model (e.g., "GPT-4o")
4. Click **"Deploy"** → choose **"Serverless API"** (MaaS) or **"Managed compute"**
5. Name the deployment (e.g., `gpt-4o`, `claude-35-sonnet`, `mistral-large`)
6. Click **"Deploy"** → wait for deployment to complete
7. Go to the deployment → **"Consume"** tab → copy the **Endpoint URL** and **API Key**

### Step 3: Configure Environment Variables

Add the following to your `.env` file:

```env
# GPT-4o (default model)
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-10-21

# Claude 3.5 Sonnet (via Azure AI Foundry)
AZURE_CLAUDE_ENDPOINT=https://<your-claude-endpoint>.inference.ai.azure.com
AZURE_CLAUDE_API_KEY=<your-claude-key>
AZURE_CLAUDE_DEPLOYMENT_NAME=claude-35-sonnet
AZURE_CLAUDE_API_VERSION=2024-10-21

# Mistral Large (via Azure AI Foundry)
AZURE_MISTRAL_ENDPOINT=https://<your-mistral-endpoint>.inference.ai.azure.com
AZURE_MISTRAL_API_KEY=<your-mistral-key>
AZURE_MISTRAL_DEPLOYMENT_NAME=mistral-large
AZURE_MISTRAL_API_VERSION=2024-10-21
```

> **Note**: You only need to configure the models you plan to use. The UI will mark unconfigured models as unavailable.

---

## 2. Azure Cosmos DB — Session Storage

### Step 1: Create a Cosmos DB Account

1. Go to [Azure Portal](https://portal.azure.com) → search **"Azure Cosmos DB"**
2. Click **"+ Create"** → select **"Azure Cosmos DB for NoSQL"**
3. Fill in:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: `phoenix-rg` (same as above)
   - **Account name**: `phoenix-cosmos-db`
   - **Region**: `East US`
   - **Capacity mode**: **Serverless** (recommended for development)
4. Click **Review + Create** → **Create**

### Step 2: Get Connection Details

1. Go to your Cosmos DB account → **"Settings"** → **"Keys"**
2. Copy the **URI** and **Primary Key**

### Step 3: Configure Environment Variables

Add to your `.env`:

```env
# Azure Cosmos DB
AZURE_COSMOS_ENDPOINT=https://phoenix-cosmos-db.documents.azure.com:443/
AZURE_COSMOS_KEY=<your-cosmos-primary-key>
AZURE_COSMOS_DB_NAME=phoenix
```

> **Note**: The database and containers will be created automatically on first run. If Cosmos DB is not configured, Phoenix falls back to an in-memory store (data is lost on restart).

---

## 3. Azure App Service — Deployment (Optional)

### Step 1: Create an App Service

1. Go to [Azure Portal](https://portal.azure.com) → search **"App Services"**
2. Click **"+ Create"** → **"Web App"**
3. Fill in:
   - **Name**: `phoenix-web-app`
   - **Runtime stack**: `Python 3.10`
   - **Region**: `East US`
   - **Pricing plan**: `B1` (Basic) or higher
4. Click **Review + Create** → **Create**

### Step 2: Configure Deployment

1. Go to your App Service → **"Settings"** → **"Configuration"**
2. Add all the environment variables from your `.env` file as **Application Settings**
3. Set the **Startup Command**: `gunicorn --worker-class eventlet -w 1 app:app`
4. Go to **"Deployment Center"** → connect to your GitHub repo
5. Configure **GitHub Actions** deployment for the `main` branch

### Step 3: Build Frontend for Production

```bash
cd web
npm run build
```

The build output will be in `web/dist/`. Configure Flask to serve these static files in production.

---

## 4. GitHub Token — For PR Creation

To enable the "Create Pull Request" feature:

1. Go to [GitHub Settings → Tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Set:
   - **Note**: `Phoenix Test Suite Generator`
   - **Expiration**: 90 days (or your preference)
   - **Scopes**: Check **`repo`** (full control of private repositories)
4. Click **"Generate token"** → copy the token

> **Security**: The token is entered per-session in the UI and is never stored. For production, consider using GitHub Apps for more secure, fine-grained access.

---

## Quick Start (Development)

After configuring your `.env` file:

```bash
# Terminal 1: Start the backend
cd /home/pprakash/phoenix
source .venv/bin/activate
pip install -r requirements.txt
python app.py

# Terminal 2: Start the frontend
cd /home/pprakash/phoenix/web
npm run dev
```

Then open **http://localhost:5173** in your browser.
