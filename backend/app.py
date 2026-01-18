from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sqlite3
from datetime import datetime
import json
import base64
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from openai import OpenAI

# Try to import OCR libraries (optional, for fallback)
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Try to import OCR libraries (optional, for fallback)
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
# Model to use - can be overridden via environment variable
# Default to gpt-4o-mini which supports vision and user has access to
DEFAULT_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# Database setup
def init_db():
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    
    # SalesOrderHeader table
    c.execute('''
        CREATE TABLE IF NOT EXISTS SalesOrderHeader (
            OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderNumber TEXT UNIQUE,
            CustomerName TEXT,
            CustomerAddress TEXT,
            OrderDate TEXT,
            DueDate TEXT,
            TotalAmount REAL,
            TaxAmount REAL,
            SubTotal REAL,
            Status TEXT,
            CreatedAt TEXT,
            UpdatedAt TEXT
        )
    ''')
    
    # SalesOrderDetail table
    c.execute('''
        CREATE TABLE IF NOT EXISTS SalesOrderDetail (
            DetailID INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderID INTEGER,
            LineNumber INTEGER,
            ProductName TEXT,
            ProductCode TEXT,
            Quantity REAL,
            UnitPrice REAL,
            LineTotal REAL,
            FOREIGN KEY (OrderID) REFERENCES SalesOrderHeader(OrderID)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_image(image_path):
    """Extract text from image using OpenAI Vision API or OCR + GPT"""
    # List of models to try in order of preference
    # Using models that user actually has access to
    models_to_try = [
        DEFAULT_MODEL,  # gpt-4o-mini (supports vision)
        'gpt-4o-mini',  # Explicitly include
        'gpt-40',  # Might be gpt-4o variant
        'gpt-5-chat-latest',  # GPT-5 chat model
        'gpt-5',  # GPT-5 base model
        'gpt-5-2025-08-07',  # GPT-5 dated version
        'gpt-5-mini',  # GPT-5 mini
        'gpt-5-mini-2025-08-07',  # GPT-5 mini dated version
        'gpt-5-nano',  # GPT-5 nano
        'gpt-5-nano-2025-08-07',  # GPT-5 nano dated version
    ]
    
    # Remove duplicates while preserving order
    models_to_try = list(dict.fromkeys(models_to_try))
    
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    last_error = None
    
    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Extract all information from this invoice image and return it as a JSON object with the following structure:
{
    "orderNumber": "string",
    "customerName": "string",
    "customerAddress": "string",
    "orderDate": "YYYY-MM-DD",
    "dueDate": "YYYY-MM-DD or null",
    "subTotal": number,
    "taxAmount": number,
    "totalAmount": number,
    "items": [
        {
            "lineNumber": number,
            "productName": "string",
            "productCode": "string",
            "quantity": number,
            "unitPrice": number,
            "lineTotal": number
        }
    ]
}
Return ONLY valid JSON, no additional text."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            content = content.strip()
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response from {model}: {str(e)}")
            print(f"Response content: {content[:500]}")  # Print first 500 chars for debugging
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            last_error = error_msg
            print(f"Error with model {model}: {error_msg}")
            # If it's a model access error, try next model
            if "model" in error_msg.lower() or "403" in error_msg or "access" in error_msg.lower() or "not have access" in error_msg.lower():
                print(f"Model {model} not available, trying next model...")
                continue
            # For other errors, raise immediately
            raise
    
    # If we get here, all vision models failed
    # Try OCR + GPT-5-pro as fallback (since user has GPT-5 access)
    print("Vision models failed, trying OCR + GPT-5-pro fallback...")
    try:
        return extract_with_ocr_and_gpt5(image_path)
    except Exception as e:
        raise ValueError(
            f"All extraction methods failed. Last vision error: {last_error}. "
            f"OCR fallback error: {str(e)}. "
            f"Please check your OpenAI project settings at https://platform.openai.com/account/limits"
        )

def extract_with_ocr_and_gpt5(image_path):
    """Fallback: Use OCR to extract text, then GPT-5 to structure it"""
    if not OCR_AVAILABLE:
        raise ValueError(
            "OCR fallback requires pytesseract. Install it with: pip install pytesseract. "
            "Also install Tesseract OCR: https://github.com/tesseract-ocr/tesseract"
        )
    
    try:
        # Extract text using OCR
        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image)
        
        if not extracted_text.strip():
            raise ValueError("OCR could not extract any text from the image")
        
        print(f"OCR extracted {len(extracted_text)} characters")
        
        # Use GPT-5 model to structure the extracted text
        # Try GPT-5 models in order of preference
        gpt5_models = ['gpt-5-chat-latest', 'gpt-5', 'gpt-5-mini', 'gpt-5-nano']
        model_used = None
        response = None
        
        for gpt5_model in gpt5_models:
            try:
                response = client.chat.completions.create(
                    model=gpt5_model,
                    messages=[
                {
                    "role": "user",
                    "content": f"""Extract invoice information from the following OCR-extracted text and return it as a JSON object with the following structure:
{{
    "orderNumber": "string",
    "customerName": "string",
    "customerAddress": "string",
    "orderDate": "YYYY-MM-DD",
    "dueDate": "YYYY-MM-DD or null",
    "subTotal": number,
    "taxAmount": number,
    "totalAmount": number,
    "items": [
        {{
            "lineNumber": number,
            "productName": "string",
            "productCode": "string",
            "quantity": number,
            "unitPrice": number,
            "lineTotal": number
        }}
    ]
}}

OCR Text:
{extracted_text}

Return ONLY valid JSON, no additional text."""
                }
                    ],
                    max_tokens=2000
                )
                model_used = gpt5_model
                break
            except Exception as e:
                error_msg = str(e)
                if "403" in error_msg or "not have access" in error_msg.lower() or "not found" in error_msg.lower():
                    continue  # Try next model
                else:
                    raise  # Other errors should be raised
        
        if not model_used or not response:
            raise ValueError("None of the available GPT-5 models could process the text")
        
        print(f"Using {model_used} for text structuring")
        content = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]
        content = content.strip()
        
        return json.loads(content)
    except Exception as e:
        raise ValueError(f"OCR + GPT-5 extraction failed: {str(e)}")

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract data using LLM
            extracted_data = extract_text_from_image(filepath)
            
            # Save to database
            conn = sqlite3.connect('invoices.db')
            c = conn.cursor()
            
            # Insert into SalesOrderHeader
            now = datetime.now().isoformat()
            c.execute('''
                INSERT INTO SalesOrderHeader 
                (OrderNumber, CustomerName, CustomerAddress, OrderDate, DueDate, 
                 TotalAmount, TaxAmount, SubTotal, Status, CreatedAt, UpdatedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                extracted_data.get('orderNumber', ''),
                extracted_data.get('customerName', ''),
                extracted_data.get('customerAddress', ''),
                extracted_data.get('orderDate', ''),
                extracted_data.get('dueDate'),
                extracted_data.get('totalAmount', 0),
                extracted_data.get('taxAmount', 0),
                extracted_data.get('subTotal', 0),
                'Pending',
                now,
                now
            ))
            
            order_id = c.lastrowid
            
            # Insert into SalesOrderDetail
            for item in extracted_data.get('items', []):
                c.execute('''
                    INSERT INTO SalesOrderDetail 
                    (OrderID, LineNumber, ProductName, ProductCode, Quantity, UnitPrice, LineTotal)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    order_id,
                    item.get('lineNumber', 0),
                    item.get('productName', ''),
                    item.get('productCode', ''),
                    item.get('quantity', 0),
                    item.get('unitPrice', 0),
                    item.get('lineTotal', 0)
                ))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'orderId': order_id,
                'data': extracted_data
            })
        except Exception as e:
            return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/orders', methods=['GET'])
def get_orders():
    conn = sqlite3.connect('invoices.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM SalesOrderHeader 
        ORDER BY CreatedAt DESC
    ''')
    
    orders = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return jsonify(orders)

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    conn = sqlite3.connect('invoices.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get header
    c.execute('SELECT * FROM SalesOrderHeader WHERE OrderID = ?', (order_id,))
    header = dict(c.fetchone())
    
    # Get details
    c.execute('SELECT * FROM SalesOrderDetail WHERE OrderID = ? ORDER BY LineNumber', (order_id,))
    details = [dict(row) for row in c.fetchall()]
    
    conn.close()
    
    return jsonify({
        'header': header,
        'details': details
    })

@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.json
    
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    
    # Update header
    if 'header' in data:
        header = data['header']
        c.execute('''
            UPDATE SalesOrderHeader 
            SET CustomerName = ?, CustomerAddress = ?, OrderDate = ?, DueDate = ?,
                TotalAmount = ?, TaxAmount = ?, SubTotal = ?, Status = ?, UpdatedAt = ?
            WHERE OrderID = ?
        ''', (
            header.get('CustomerName'),
            header.get('CustomerAddress'),
            header.get('OrderDate'),
            header.get('DueDate'),
            header.get('TotalAmount'),
            header.get('TaxAmount'),
            header.get('SubTotal'),
            header.get('Status'),
            datetime.now().isoformat(),
            order_id
        ))
    
    # Update details
    if 'details' in data:
        # Delete existing details
        c.execute('DELETE FROM SalesOrderDetail WHERE OrderID = ?', (order_id,))
        
        # Insert new details
        for detail in data['details']:
            c.execute('''
                INSERT INTO SalesOrderDetail 
                (OrderID, LineNumber, ProductName, ProductCode, Quantity, UnitPrice, LineTotal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_id,
                detail.get('LineNumber'),
                detail.get('ProductName'),
                detail.get('ProductCode'),
                detail.get('Quantity'),
                detail.get('UnitPrice'),
                detail.get('LineTotal')
            ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    
    # Delete details first (foreign key constraint)
    c.execute('DELETE FROM SalesOrderDetail WHERE OrderID = ?', (order_id,))
    c.execute('DELETE FROM SalesOrderHeader WHERE OrderID = ?', (order_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    import sys
    # Fix for Windows debug mode issue
    if sys.platform == 'win32':
        app.run(debug=True, port=5000, use_reloader=False)
    else:
        app.run(debug=True, port=5000)
