# ForgeOS

Welcome to ForgeOS! This project consists of a React/Vite frontend and a FastAPI/Python backend that orchestrates integrations via the Model Context Protocol (MCP).

## Prerequisites
- **Node.js** (v18+)
- **Python** (v3.10+)
- **PostgreSQL** (Neon DB or local)

---

## 🚀 Running the Backend

The backend is built with Python and FastAPI.

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Activate the virtual environment:**
   - **Windows:** `venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`

3. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Ensure you have a `.env` file in the `backend/` directory with the following keys:
   ```env
   DATABASE_URL="postgresql://..."
   SECRET_KEY="your_secret_key"
   GEMINI_API_KEY="your_gemini_key"
   GITHUB_CLIENT_ID="..."
   GITHUB_CLIENT_SECRET="..."
   GOOGLE_CLIENT_ID="..."
   GOOGLE_CLIENT_SECRET="..."
   MASTER_ENCRYPTION_KEY="..."
   ```

5. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend API will run on `http://localhost:8000`.

---

## 🎨 Running the Frontend

The frontend is a modern React application built with Vite and TailwindCSS.

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   The frontend will run on `http://localhost:5173`.

---

## 🔧 Architecture & Integrations
- **Authentication:** Uses OAuth via Authlib.
- **Database:** SQLAlchemy mapped to a PostgreSQL database.
- **Execution Engine:** Uses the Model Context Protocol (MCP) to securely execute tools across platforms (GitHub, Google Workspace, etc.).
- **Planning Engine:** Powered by LangChain and the Gemini API.
