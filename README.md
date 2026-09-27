# SmartInvoice AI 🧾

SmartInvoice AI is an AI-powered invoice automation system that converts natural-language customer requests into structured invoice data.

## Features

- Natural-language customer input
- AI-powered extraction of customer and service details
- Automatic service and quantity detection
- CSV-based price lookup
- Accurate invoice calculations
- Missing-service detection
- Invoice review and approval workflow
- PDF invoice generation and download

## Technology Stack

- Python
- Streamlit
- Google Gemini API
- CSV
- ReportLab

## How It Works

1. Customer enters a natural-language invoice request.
2. Gemini AI extracts customer details and requested services.
3. Service prices are retrieved from the CSV price database.
4. Invoice totals are calculated automatically.
5. User reviews and approves the invoice.
6. A professional PDF invoice can be downloaded.

## Example

Customer request:

"Create an invoice for Rahul Sharma, email rahul@gmail.com. He needs 2 Website Design packages and 1 SEO Package."

The system extracts the services, retrieves their prices from the database, calculates the subtotal, and generates the invoice.