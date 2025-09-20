"""
PDF Invoice Generation Utility

This module handles the generation of professional PDF invoices using ReportLab.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

from src.models.models import Invoice, BusinessSettings


class PDFInvoiceGenerator:
    def __init__(self, business_settings: BusinessSettings):
        self.business_settings = business_settings
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles for the invoice"""
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))

        self.styles.add(ParagraphStyle(
            name='BusinessName',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            alignment=TA_LEFT,
            textColor=colors.black
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor=colors.darkblue
        ))

        self.styles.add(ParagraphStyle(
            name='Normal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            alignment=TA_LEFT
        ))

        self.styles.add(ParagraphStyle(
            name='RightAlign',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT
        ))

    def generate_invoice_pdf(self, invoice: Invoice, output_path: str = None) -> str:
        """
        Generate a PDF invoice and return the file path

        Args:
            invoice: Invoice object containing all invoice data
            output_path: Optional custom output path

        Returns:
            str: Path to the generated PDF file
        """
        if not output_path:
            # Create exports directory if it doesn't exist
            exports_dir = Path("data/exports/invoices")
            exports_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"invoice_{timestamp}.pdf"
            output_path = exports_dir / filename

        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build content
        story = []

        # Header with business info and logo
        story.extend(self._build_header())
        story.append(Spacer(1, 20))

        # Invoice title and details
        story.extend(self._build_invoice_details(invoice))
        story.append(Spacer(1, 20))

        # Customer details
        story.extend(self._build_customer_details(invoice))
        story.append(Spacer(1, 20))

        # Invoice items table
        story.extend(self._build_items_table(invoice))
        story.append(Spacer(1, 20))

        # Totals section
        story.extend(self._build_totals_section(invoice))
        story.append(Spacer(1, 20))

        # Footer with terms and notes
        story.extend(self._build_footer(invoice))

        # Build PDF
        doc.build(story)

        return str(output_path)

    def _build_header(self):
        """Build the header section with business information"""
        elements = []

        # Business name
        business_name = Paragraph(
            self.business_settings.business_name,
            self.styles['BusinessName']
        )
        elements.append(business_name)

        # Business address and contact info
        if self.business_settings.business_address:
            address = Paragraph(
                self.business_settings.business_address,
                self.styles['Normal']
            )
            elements.append(address)

        contact_info = []
        if self.business_settings.business_phone:
            contact_info.append(f"Phone: {self.business_settings.business_phone}")
        if self.business_settings.business_email:
            contact_info.append(f"Email: {self.business_settings.business_email}")
        if self.business_settings.business_gstin:
            contact_info.append(f"GSTIN: {self.business_settings.business_gstin}")

        if contact_info:
            contact_text = " | ".join(contact_info)
            contact_para = Paragraph(contact_text, self.styles['Normal'])
            elements.append(contact_para)

        return elements

    def _build_invoice_details(self, invoice: Invoice):
        """Build invoice number, date, and status section"""
        elements = []

        # Invoice title
        title = Paragraph("INVOICE", self.styles['InvoiceTitle'])
        elements.append(title)

        # Create table for invoice details
        details_data = [
            ['Invoice Number:', invoice.invoice_number],
            ['Invoice Date:', invoice.date],
            ['Due Date:', invoice.due_date or 'N/A'],
            ['Status:', invoice.status.title()]
        ]

        details_table = Table(details_data, colWidths=[2*inch, 2*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(details_table)
        return elements

    def _build_customer_details(self, invoice: Invoice):
        """Build customer information section"""
        elements = []

        # Section header
        header = Paragraph("Bill To:", self.styles['SectionHeader'])
        elements.append(header)

        # Customer details
        customer_lines = [invoice.customer_name]
        if invoice.customer_address:
            customer_lines.append(invoice.customer_address)
        if invoice.customer_email:
            customer_lines.append(f"Email: {invoice.customer_email}")
        if invoice.customer_gstin:
            customer_lines.append(f"GSTIN: {invoice.customer_gstin}")

        customer_text = "<br/>".join(customer_lines)
        customer_para = Paragraph(customer_text, self.styles['Normal'])
        elements.append(customer_para)

        return elements

    def _build_items_table(self, invoice: Invoice):
        """Build the items table"""
        elements = []

        # Table headers
        headers = ['Description', 'Qty', 'Rate', 'Discount%', 'Amount']
        table_data = [headers]

        # Add items
        for item in invoice.items:
            row = [
                item.name,
                f"{item.quantity:,.2f}",
                f"{self.business_settings.currency_symbol}{item.unit_price:,.2f}",
                f"{item.discount_rate:,.1f}%",
                f"{self.business_settings.currency_symbol}{item.line_total:,.2f}"
            ]
            table_data.append(row)

        # Create table
        items_table = Table(table_data, colWidths=[3*inch, 0.8*inch, 1*inch, 0.8*inch, 1.2*inch])

        # Style the table
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Description left-aligned
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]

        # Alternate row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgrey))

        items_table.setStyle(TableStyle(table_style))
        elements.append(items_table)

        return elements

    def _build_totals_section(self, invoice: Invoice):
        """Build the totals section"""
        elements = []

        # Totals data
        totals_data = []

        # Subtotal
        totals_data.append(['Subtotal:', f"{self.business_settings.currency_symbol}{invoice.subtotal:,.2f}"])

        # Global discount if applicable
        if invoice.global_discount_amount > 0:
            totals_data.append([
                f'Discount ({invoice.global_discount_rate:,.1f}%):',
                f"-{self.business_settings.currency_symbol}{invoice.global_discount_amount:,.2f}"
            ])

        # Tax
        if invoice.total_tax > 0:
            totals_data.append(['Tax:', f"{self.business_settings.currency_symbol}{invoice.total_tax:,.2f}"])

        # Grand total
        totals_data.append(['Total:', f"{self.business_settings.currency_symbol}{invoice.grand_total:,.2f}"])

        # Create totals table
        totals_table = Table(totals_data, colWidths=[4*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -2), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.darkblue),
        ]))

        elements.append(totals_table)
        return elements

    def _build_footer(self, invoice: Invoice):
        """Build footer with terms and notes"""
        elements = []

        # Notes
        if invoice.notes:
            notes_header = Paragraph("Notes:", self.styles['SectionHeader'])
            elements.append(notes_header)
            notes_para = Paragraph(invoice.notes, self.styles['Normal'])
            elements.append(notes_para)
            elements.append(Spacer(1, 12))

        # Terms and conditions
        if invoice.terms or self.business_settings.terms_and_conditions:
            terms_text = invoice.terms or self.business_settings.terms_and_conditions
            terms_header = Paragraph("Terms & Conditions:", self.styles['SectionHeader'])
            elements.append(terms_header)
            terms_para = Paragraph(terms_text, self.styles['Normal'])
            elements.append(terms_para)
            elements.append(Spacer(1, 12))

        # Footer message
        if self.business_settings.notes_footer:
            footer_para = Paragraph(
                self.business_settings.notes_footer,
                self.styles['Normal']
            )
            elements.append(footer_para)

        return elements