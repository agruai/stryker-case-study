# Invoice Extraction App

A full-stack document extraction application that uses AI to extract structured data from invoice images. Built with React/Next.js frontend and Flask backend, integrated with OpenAI's Vision API for intelligent document processing.

## Features

- 📄 **Document Upload**: Drag-and-drop or click to upload invoice images (PNG, JPG, PDF)
- 🤖 **AI-Powered Extraction**: Uses OpenAI GPT-4 Vision API to extract structured data from invoices
- 💾 **Database Storage**: SQLite database with SalesOrderHeader and SalesOrderDetail tables
- ✏️ **Edit & Update**: View, edit, and save extracted invoice data
- 🎨 **Modern UI**: Clean, responsive interface with real-time updates
- 📊 **Multiple Templates**: Handles various invoice formats and layouts

## Project Structure

```
Stryker/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── requirements.txt       # Python dependencies
│   ├── create_sample_invoices.py  # Script to generate test invoices
│   └── uploads/               # Uploaded invoice files
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Main application page
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

## Prerequisites

- Python 3.8+
- Node.js 18+
- OpenAI API key
- npm or yarn

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

5. (Optional) Generate sample invoices for testing:
```bash
python create_sample_invoices.py
```

6. Start the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file (optional, defaults to localhost:5000):
```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

4. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Usage

1. **Upload an Invoice**: 
   - Drag and drop an invoice image onto the upload area, or
   - Click "Select File" to choose an invoice image

2. **View Extracted Data**:
   - The app automatically processes the invoice using AI
   - Extracted data appears in the "Extracted Invoices" table

3. **Edit Invoice Data**:
   - Click "View" on any invoice to see full details
   - Click "Edit" to modify fields
   - Save changes or delete invoices as needed

## Database Schema

### SalesOrderHeader
- `OrderID` (Primary Key)
- `OrderNumber` (Unique)
- `CustomerName`
- `CustomerAddress`
- `OrderDate`
- `DueDate`
- `TotalAmount`
- `TaxAmount`
- `SubTotal`
- `Status`
- `CreatedAt`
- `UpdatedAt`

### SalesOrderDetail
- `DetailID` (Primary Key)
- `OrderID` (Foreign Key)
- `LineNumber`
- `ProductName`
- `ProductCode`
- `Quantity`
- `UnitPrice`
- `LineTotal`

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/upload` - Upload and process invoice
- `GET /api/orders` - Get all orders
- `GET /api/orders/<id>` - Get specific order with details
- `PUT /api/orders/<id>` - Update order
- `DELETE /api/orders/<id>` - Delete order

## Scaling Strategies

### 1. **Performance Optimization**

**Current State**: Single-threaded Flask server, synchronous processing

**Scaling Approach**:
- **Async Processing**: Implement Celery with Redis/RabbitMQ for background task processing
  - Upload endpoint returns immediately with job ID
  - Client polls for completion or uses WebSockets for real-time updates
  - Allows handling multiple uploads concurrently

- **Caching**: 
  - Redis cache for frequently accessed orders
  - Cache extracted data to avoid re-processing

- **Database Optimization**:
  - Add indexes on frequently queried fields (OrderNumber, CustomerName, OrderDate)
  - Consider connection pooling (SQLAlchemy with connection pool)
  - Migrate to PostgreSQL for production (better concurrency, ACID compliance)

### 2. **Architecture Evolution**

**Current State**: Monolithic Flask app, SQLite database

**Scaling Approach**:
- **Microservices Architecture**:
  - Separate services: Upload Service, Extraction Service, Data Service
  - API Gateway (Kong, AWS API Gateway) for routing
  - Service mesh for inter-service communication

- **Message Queue System**:
  - RabbitMQ or AWS SQS for async processing
  - Dead letter queues for failed extractions
  - Priority queues for urgent documents

- **Containerization**:
  - Docker containers for each service
  - Kubernetes for orchestration
  - Auto-scaling based on queue depth

### 3. **Storage & File Management**

**Current State**: Local file storage

**Scaling Approach**:
- **Object Storage**: 
  - AWS S3, Azure Blob Storage, or Google Cloud Storage
  - CDN (CloudFront) for fast file delivery
  - Lifecycle policies for archival

- **Database Scaling**:
  - Read replicas for query distribution
  - Sharding by customer or date range
  - Consider NoSQL (MongoDB) for flexible schema if document types vary significantly

### 4. **AI/ML Enhancements**

**Current State**: Single OpenAI API call per document

**Scaling Approach**:
- **Multi-Provider Strategy**:
  - Support multiple LLM providers (OpenAI, Anthropic, Google)
  - Fallback mechanisms if one provider is down
  - Cost optimization by routing to cheapest provider

- **Fine-Tuning**:
  - Fine-tune models on company-specific invoice formats
  - Reduce API costs and improve accuracy

- **Pre-processing**:
  - OCR preprocessing (Tesseract, AWS Textract) for better text extraction
  - Image enhancement before sending to LLM
  - Template matching for known invoice formats

### 5. **Additional Document Types**

**Current State**: Invoice-focused

**Scaling Approach**:
- **Document Classification**:
  - ML model to classify document type (invoice, receipt, purchase order, etc.)
  - Route to appropriate extraction pipeline

- **Flexible Schema**:
  - JSON schema validation per document type
  - Dynamic form generation based on document type
  - Configurable extraction prompts per document type

### 6. **Monitoring & Observability**

**Scaling Approach**:
- **Logging**: 
  - Structured logging (JSON format)
  - Centralized logging (ELK stack, CloudWatch, Datadog)

- **Metrics**:
  - Processing time, success rate, API costs
  - Database query performance
  - Queue depth and processing rate

- **Alerting**:
  - Failed extractions, API errors, queue backup
  - Cost thresholds for AI API usage

### 7. **Security & Compliance**

**Scaling Approach**:
- **Authentication & Authorization**:
  - JWT tokens, OAuth 2.0
  - Role-based access control (RBAC)
  - Multi-tenant isolation

- **Data Protection**:
  - Encryption at rest and in transit
  - PII detection and redaction
  - GDPR/CCPA compliance features
  - Audit logging

### 8. **Cost Optimization**

**Scaling Approach**:
- **API Cost Management**:
  - Batch processing during off-peak hours
  - Caching similar invoices
  - Rate limiting to prevent abuse

- **Infrastructure**:
  - Auto-scaling to match demand
  - Spot instances for non-critical workloads
  - Reserved instances for baseline capacity

## Production Deployment Checklist

- [ ] Replace SQLite with PostgreSQL
- [ ] Implement authentication/authorization
- [ ] Set up CI/CD pipeline
- [ ] Add comprehensive error handling
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategies
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Implement request validation
- [ ] Add unit and integration tests
- [ ] Set up staging environment
- [ ] Configure SSL/TLS certificates
- [ ] Implement logging and audit trails

## Technologies Used

- **Frontend**: Next.js 14, React 18, TypeScript, Axios
- **Backend**: Flask, Python, SQLite
- **AI/ML**: OpenAI GPT-4 Vision API
- **Styling**: CSS3 with modern gradients and animations

## License

This project is created for demonstration purposes.

## Support

For questions or issues, please refer to the codebase or contact the development team.
