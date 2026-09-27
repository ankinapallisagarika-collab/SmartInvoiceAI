import os
import json
import csv
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from google import genai

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# -----------------------------
# Load API key
# -----------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


# -----------------------------
# Load price database
# -----------------------------

with open("prices.csv", newline="", encoding="utf-8") as file:
    prices = list(csv.DictReader(file))


# -----------------------------
# PDF generation function
# -----------------------------

def create_invoice_pdf(
    customer_name,
    customer_email,
    services,
    subtotal
):

    buffer = BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    # Title
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(50, height - 60, "SMARTINVOICE AI")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, height - 85, "AI-Powered Invoice")

    # Customer details
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 130, "Customer Details")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(
        50,
        height - 150,
        f"Name: {customer_name}"
    )

    pdf.drawString(
        50,
        height - 170,
        f"Email: {customer_email}"
    )

    # Invoice table heading
    y = height - 220

    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(50, y, "Service")
    pdf.drawString(300, y, "Quantity")
    pdf.drawString(380, y, "Unit Price")
    pdf.drawString(480, y, "Total")

    y -= 20

    pdf.setFont("Helvetica", 10)

    for item in services:

        service_name = item["service"]
        quantity = item["quantity"]
        unit_price = item["unit_price"]
        line_total = item["line_total"]

        pdf.drawString(
            50,
            y,
            service_name
        )

        pdf.drawString(
            300,
            y,
            str(quantity)
        )

        pdf.drawString(
            380,
            y,
            f"Rs. {unit_price:,.2f}"
        )

        pdf.drawString(
            480,
            y,
            f"Rs. {line_total:,.2f}"
        )

        y -= 25

    # Total
    y -= 20

    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(
        350,
        y,
        f"Subtotal: Rs. {subtotal:,.2f}"
    )

    y -= 40

    pdf.setFont("Helvetica", 10)

    pdf.drawString(
        50,
        y,
        "Generated using SmartInvoice AI"
    )

    pdf.save()

    buffer.seek(0)

    return buffer


# -----------------------------
# Page settings
# -----------------------------

st.set_page_config(
    page_title="SmartInvoice AI",
    page_icon="🧾"
)

st.title("🧾 SmartInvoice AI")

st.subheader(
    "AI-Powered Invoice Automation System"
)

st.write(
    "Create invoices from simple natural-language customer requests."
)


# -----------------------------
# Customer request
# -----------------------------

customer_request = st.text_area(
    "Customer Request",
    placeholder=(
        "Example: Create an invoice for Rahul Sharma. "
        "He needs 2 Website Design packages and 1 SEO Package."
    )
)


# -----------------------------
# Generate Invoice
# -----------------------------

if st.button("Generate Invoice"):

    if customer_request.strip():

        prompt = f"""
You are an invoice assistant.

Extract the following information:

1. Customer name
2. Customer email
3. Requested services
4. Quantity for each service
5. Notes

Important:
If the customer says "Website Design packages",
return the service name as "Website Design".

Return ONLY valid JSON in exactly this format:

{{
    "customer_name": "",
    "customer_email": "",
    "services": [
        {{
            "service": "",
            "quantity": 0
        }}
    ],
    "notes": ""
}}

Customer request:
{customer_request}
"""

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

            result = json.loads(response.text)

            st.session_state["invoice_result"] = result

        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )


# -----------------------------
# Display invoice
# -----------------------------

if "invoice_result" in st.session_state:

    result = st.session_state["invoice_result"]

    st.success(
        "AI successfully understood the request!"
    )

    st.subheader("📋 Extracted Information")

    st.write(
        "**Customer Name:**",
        result["customer_name"]
    )

    st.write(
        "**Email:**",
        result["customer_email"]
    )

    st.write("**Services:**")

    invoice_services = []
    subtotal = 0
    missing_services = []

    for service in result["services"]:

        st.write(
            f"- {service['service']} × "
            f"{service['quantity']}"
        )

        service_name = (
            service["service"]
            .strip()
            .lower()
        )

        quantity = int(service["quantity"])

        match = [
            row for row in prices
            if row["service_name"]
            .strip()
            .lower()
            == service_name
        ]

        if not match:

            missing_services.append(
                service["service"]
            )

            continue

        unit_price = float(
            match[0]["price"]
        )

        line_total = quantity * unit_price

        subtotal += line_total

        invoice_services.append(
            {
                "service": service["service"],
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": line_total
            }
        )

    # -----------------------------
    # Price details
    # -----------------------------

    st.subheader("💰 Price Details")

    for item in invoice_services:

        st.write(
            f"{item['service']} — "
            f"{item['quantity']} × "
            f"₹{item['unit_price']:,.2f} = "
            f"₹{item['line_total']:,.2f}"
        )

    if missing_services:

        st.warning(
            "Service(s) not found in price database: "
            + ", ".join(missing_services)
        )

    else:

        st.success(
            f"Subtotal: ₹{subtotal:,.2f}"
        )

        # -----------------------------
        # Review and approval
        # -----------------------------

        st.subheader("🔍 Review & Approval")

        approved = st.checkbox(
            "I have reviewed the invoice details and approve this invoice."
        )

        if approved:

            pdf_file = create_invoice_pdf(
                result["customer_name"],
                result["customer_email"],
                invoice_services,
                subtotal
            )

            st.success(
                "Invoice approved successfully!"
            )

            st.download_button(
                label="📄 Download Invoice PDF",
                data=pdf_file,
                file_name="SmartInvoice_Invoice.pdf",
                mime="application/pdf"
            )