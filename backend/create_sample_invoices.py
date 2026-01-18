"""
Script to create sample invoice images for testing
Run this script to generate example invoices with different templates
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_invoice_template_1(output_path):
    """Create a modern, clean invoice template"""
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        title_font = ImageFont.truetype("arial.ttf", 32)
        header_font = ImageFont.truetype("arial.ttf", 18)
        body_font = ImageFont.truetype("arial.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
    
    # Header
    draw.rectangle([0, 0, 800, 120], fill='#667eea', outline=None)
    draw.text((50, 30), "INVOICE", fill='white', font=title_font)
    draw.text((50, 80), "Order #: INV-2024-001", fill='white', font=body_font)
    
    # Company Info
    y = 150
    draw.text((50, y), "From:", font=header_font, fill='black')
    draw.text((50, y + 25), "Tech Solutions Inc.", font=body_font, fill='black')
    draw.text((50, y + 45), "123 Business St, San Francisco, CA 94102", font=body_font, fill='black')
    
    # Customer Info
    y = 150
    draw.text((450, y), "Bill To:", font=header_font, fill='black')
    draw.text((450, y + 25), "Acme Corporation", font=body_font, fill='black')
    draw.text((450, y + 45), "456 Corporate Ave, New York, NY 10001", font=body_font, fill='black')
    
    # Invoice Details
    y = 280
    draw.text((50, y), "Invoice Date: 2024-01-15", font=body_font, fill='black')
    draw.text((450, y), "Due Date: 2024-02-15", font=body_font, fill='black')
    
    # Table Header
    y = 330
    draw.rectangle([50, y, 750, y + 30], fill='#f0f0f0', outline='black')
    draw.text((70, y + 8), "Item", font=header_font, fill='black')
    draw.text((200, y + 8), "Code", font=header_font, fill='black')
    draw.text((300, y + 8), "Qty", font=header_font, fill='black')
    draw.text((400, y + 8), "Price", font=header_font, fill='black')
    draw.text((550, y + 8), "Total", font=header_font, fill='black')
    
    # Items
    items = [
        ("Laptop Computer", "LAP-001", 2, 1299.99, 2599.98),
        ("Wireless Mouse", "MSE-205", 5, 29.99, 149.95),
        ("USB-C Cable", "CBL-310", 10, 19.99, 199.90),
    ]
    
    y = 360
    for item in items:
        draw.text((70, y), item[0], font=body_font, fill='black')
        draw.text((200, y), item[1], font=body_font, fill='black')
        draw.text((300, y), str(item[2]), font=body_font, fill='black')
        draw.text((400, y), f"${item[3]:.2f}", font=body_font, fill='black')
        draw.text((550, y), f"${item[4]:.2f}", font=body_font, fill='black')
        draw.line([50, y + 25, 750, y + 25], fill='gray', width=1)
        y += 30
    
    # Totals
    y += 20
    subtotal = sum(item[4] for item in items)
    tax = subtotal * 0.08
    total = subtotal + tax
    
    draw.text((550, y), f"Subtotal: ${subtotal:.2f}", font=body_font, fill='black')
    y += 25
    draw.text((550, y), f"Tax (8%): ${tax:.2f}", font=body_font, fill='black')
    y += 25
    draw.rectangle([530, y - 5, 750, y + 30], outline='black', width=2)
    draw.text((550, y), f"Total: ${total:.2f}", font=header_font, fill='black')
    
    img.save(output_path)
    print(f"Created invoice: {output_path}")

def create_invoice_template_2(output_path):
    """Create a traditional invoice template"""
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 28)
        header_font = ImageFont.truetype("arial.ttf", 16)
        body_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
    
    # Header with border
    draw.rectangle([20, 20, 780, 100], outline='black', width=2)
    draw.text((40, 40), "SALES INVOICE", font=title_font, fill='black')
    draw.text((40, 70), "Invoice Number: SO-2024-042", font=body_font, fill='black')
    
    # Company and Customer side by side
    y = 120
    draw.text((40, y), "Vendor:", font=header_font, fill='black')
    draw.text((40, y + 20), "Global Manufacturing Co.", font=body_font, fill='black')
    draw.text((40, y + 40), "789 Industrial Blvd", font=body_font, fill='black')
    draw.text((40, y + 60), "Chicago, IL 60601", font=body_font, fill='black')
    
    draw.text((400, y), "Customer:", font=header_font, fill='black')
    draw.text((400, y + 20), "Retail Partners LLC", font=body_font, fill='black')
    draw.text((400, y + 40), "321 Commerce Drive", font=body_font, fill='black')
    draw.text((400, y + 60), "Los Angeles, CA 90001", font=body_font, fill='black')
    
    # Dates
    y = 220
    draw.text((40, y), "Invoice Date: 2024-03-20", font=body_font, fill='black')
    draw.text((400, y), "Payment Due: 2024-04-20", font=body_font, fill='black')
    
    # Items table
    y = 260
    draw.line([40, y, 760, y], fill='black', width=2)
    
    # Headers
    draw.text((50, y + 10), "Description", font=header_font, fill='black')
    draw.text((300, y + 10), "SKU", font=header_font, fill='black')
    draw.text((400, y + 10), "Qty", font=header_font, fill='black')
    draw.text((480, y + 10), "Unit $", font=header_font, fill='black')
    draw.text((580, y + 10), "Amount", font=header_font, fill='black')
    
    draw.line([40, y + 35, 760, y + 35], fill='black', width=1)
    
    items = [
        ("Office Desk Chair", "CHR-500", 8, 249.00, 1992.00),
        ("Standing Desk", "DSK-700", 3, 599.00, 1797.00),
        ("Monitor Stand", "MST-100", 12, 45.00, 540.00),
    ]
    
    y = 300
    for item in items:
        draw.text((50, y), item[0], font=body_font, fill='black')
        draw.text((300, y), item[1], font=body_font, fill='black')
        draw.text((400, y), str(item[2]), font=body_font, fill='black')
        draw.text((480, y), f"${item[3]:.2f}", font=body_font, fill='black')
        draw.text((580, y), f"${item[4]:.2f}", font=body_font, fill='black')
        draw.line([40, y + 20, 760, y + 20], fill='gray', width=1)
        y += 25
    
    # Totals
    y += 10
    subtotal = sum(item[4] for item in items)
    tax = subtotal * 0.10
    total = subtotal + tax
    
    draw.text((580, y), f"Subtotal: ${subtotal:.2f}", font=body_font, fill='black')
    y += 20
    draw.text((580, y), f"Sales Tax (10%): ${tax:.2f}", font=body_font, fill='black')
    y += 20
    draw.line([500, y, 760, y], fill='black', width=2)
    draw.text((580, y + 5), f"TOTAL: ${total:.2f}", font=header_font, fill='black')
    
    # Footer
    draw.text((40, 950), "Thank you for your business!", font=body_font, fill='black')
    draw.text((40, 970), "Payment terms: Net 30", font=body_font, fill='black')
    
    img.save(output_path)
    print(f"Created invoice: {output_path}")

def create_invoice_template_3(output_path):
    """Create a minimalist invoice template"""
    img = Image.new('RGB', (700, 900), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        header_font = ImageFont.truetype("arial.ttf", 14)
        body_font = ImageFont.truetype("arial.ttf", 11)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
    
    # Simple header
    draw.text((50, 50), "INVOICE", font=title_font, fill='black')
    draw.text((50, 85), "INV-2024-088", font=body_font, fill='gray')
    
    # Info section
    y = 130
    draw.text((50, y), "Service Provider", font=header_font, fill='black')
    draw.text((50, y + 20), "Digital Services Pro", font=body_font, fill='black')
    draw.text((50, y + 40), "555 Tech Way, Seattle, WA 98101", font=body_font, fill='black')
    
    draw.text((350, y), "Client", font=header_font, fill='black')
    draw.text((350, y + 20), "Startup Innovations", font=body_font, fill='black')
    draw.text((350, y + 40), "999 Innovation Blvd, Austin, TX 78701", font=body_font, fill='black')
    
    y = 220
    draw.text((50, y), "Date: 2024-05-10", font=body_font, fill='black')
    
    # Items
    y = 270
    items = [
        ("Web Development Services", "WEB-DEV", 40, 150.00, 6000.00),
        ("Cloud Hosting Setup", "CLD-HST", 1, 299.00, 299.00),
        ("SEO Optimization", "SEO-OPT", 1, 899.00, 899.00),
    ]
    
    for item in items:
        draw.text((50, y), f"{item[0]} ({item[1]})", font=body_font, fill='black')
        draw.text((50, y + 15), f"Qty: {item[2]} × ${item[3]:.2f} = ${item[4]:.2f}", font=body_font, fill='gray')
        y += 40
    
    # Totals
    y += 20
    subtotal = sum(item[4] for item in items)
    tax = subtotal * 0.06
    total = subtotal + tax
    
    draw.line([50, y, 650, y], fill='gray', width=1)
    y += 15
    draw.text((450, y), f"Subtotal: ${subtotal:.2f}", font=body_font, fill='black')
    y += 20
    draw.text((450, y), f"Tax (6%): ${tax:.2f}", font=body_font, fill='black')
    y += 20
    draw.text((450, y), f"Total: ${total:.2f}", font=header_font, fill='black')
    
    img.save(output_path)
    print(f"Created invoice: {output_path}")

if __name__ == "__main__":
    os.makedirs("sample_invoices", exist_ok=True)
    
    create_invoice_template_1("sample_invoices/invoice_template_1.png")
    create_invoice_template_2("sample_invoices/invoice_template_2.png")
    create_invoice_template_3("sample_invoices/invoice_template_3.png")
    
    print("\nSample invoices created in 'sample_invoices' directory!")
