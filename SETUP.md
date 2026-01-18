# Quick Setup Guide

## Step 1: Backend Setup

1. Open a terminal and navigate to the backend folder:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
# Windows (PowerShell or CMD)
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install Python dependencies:
```bash
# On Windows, always use python -m pip (pip may not be in PATH)
python -m pip install -r requirements.txt

# Mac/Linux
python3 -m pip install -r requirements.txt
# OR if pip is in PATH:
pip install -r requirements.txt
```

4. Create a `.env` file in the `backend` folder with your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here

# Optional: If gpt-4o is not available, use one of these:
# OPENAI_MODEL=gpt-4-turbo
# OPENAI_MODEL=gpt-4-vision-preview
```

5. (Optional) Generate sample invoices:
```bash
python create_sample_invoices.py
```

6. Start the Flask server:
```bash
python app.py
```

The backend should now be running on `http://localhost:5000`

## Step 2: Frontend Setup

1. Open a NEW terminal and navigate to the frontend folder:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the Next.js development server:
```bash
npm run dev
```

The frontend should now be running on `http://localhost:3000`

## Step 3: Test the Application

1. Open your browser and go to `http://localhost:3000`

2. Upload an invoice:
   - Use one of the sample invoices from `backend/sample_invoices/` (if you generated them)
   - Or use the provided `Sales Invoice.png` file
   - Or upload any invoice image

3. The app will:
   - Process the invoice using AI
   - Extract structured data
   - Display it in the table
   - Allow you to view, edit, and save changes

## Troubleshooting

### Backend Issues

- **Port 5000 already in use**: Change the port in `backend/app.py` (last line)
- **OpenAI API errors**: Check your API key in the `.env` file
- **Database errors**: Delete `invoices.db` and restart the server (it will recreate)

### Frontend Issues

- **Cannot connect to backend**: Make sure the Flask server is running on port 5000
- **CORS errors**: Ensure `flask-cors` is installed in the backend
- **Build errors**: Delete `node_modules` and `.next` folder, then run `npm install` again

## Demo Tips

1. **Show different templates**: Upload multiple invoices with different layouts to demonstrate the AI's flexibility

2. **Edit functionality**: 
   - Upload an invoice
   - Click "View" to see extracted data
   - Click "Edit" to modify fields
   - Show how changes are saved

3. **Real-time processing**: 
   - Show the loading spinner during extraction
   - Demonstrate immediate UI updates after processing

4. **Database persistence**: 
   - Upload multiple invoices
   - Refresh the page to show data persists
   - Show the SQLite database file if needed
