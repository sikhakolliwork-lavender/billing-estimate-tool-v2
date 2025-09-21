"""
Cloud-Compatible PDF Generator

This module provides PDF generation that returns bytes instead of saving files,
making it suitable for cloud deployment where file storage is not persistent.
"""

import io
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from src.models.models import Estimate, BusinessSettings


class CloudPDFEstimateGenerator:
    def __init__(self, business_settings: BusinessSettings):
        self.business_settings = business_settings
        self.styles = getSampleStyleSheet()
        self._setup_unicode_fonts()
        self._create_custom_styles()

    def _setup_unicode_fonts(self):
        """Setup Unicode font support for currency symbols"""
        try:
            # Try multiple font paths for better compatibility
            font_paths = [
                '/System/Library/Fonts/Arial Unicode MS.ttf',
                '/System/Library/Fonts/Arial.ttf',
                '/Library/Fonts/Arial.ttf',
                '/System/Library/Fonts/DejaVuSans.ttf'
            ]

            for font_path in font_paths:
                try:
                    pdfmetrics.registerFont(TTFont('UnicodeFont', font_path))
                    self.unicode_font = 'UnicodeFont'
                    break
                except:
                    continue
            else:
                # If no Unicode font found, use Helvetica
                self.unicode_font = 'Helvetica'
        except:
            # Fall back to Helvetica
            self.unicode_font = 'Helvetica'

    def _format_currency(self, amount: float) -> str:
        """Format currency amount with proper symbol encoding"""
        symbol = self.business_settings.currency_symbol
        if symbol == '₹':
            # For ₹ symbol, ensure proper encoding
            if self.unicode_font == 'UnicodeFont':
                return f"₹{amount:,.2f}"
            else:
                # Fallback to Rs. if Unicode not available
                return f"Rs.{amount:,.2f}"
        else:
            return f"{symbol}{amount:,.2f}"

    def _create_custom_styles(self):
        """Create custom paragraph styles for the estimate"""
        self.styles.add(ParagraphStyle(
            name='EstimateTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName=self.unicode_font
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
            name='CustomNormal',
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

    def generate_estimate_pdf_bytes(self, estimate: Estimate) -> bytes:
        """
        Generate a PDF estimate and return as bytes

        Args:
            estimate: Estimate object containing all estimate data

        Returns:
            bytes: PDF content as bytes
        """
        # Create a BytesIO buffer
        buffer = io.BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build content
        story = []

        # Header with business info
        story.extend(self._build_header())
        story.append(Spacer(1, 20))

        # Estimate title and details
        story.extend(self._build_estimate_details(estimate))
        story.append(Spacer(1, 20))

        # Customer details
        story.extend(self._build_customer_details(estimate))
        story.append(Spacer(1, 20))

        # Estimate items table
        story.extend(self._build_items_table(estimate))
        story.append(Spacer(1, 20))

        # Totals section
        story.extend(self._build_totals_section(estimate))
        story.append(Spacer(1, 20))

        # Footer with terms and notes
        story.extend(self._build_footer(estimate))

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

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
                self.styles['CustomNormal']
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
            contact_para = Paragraph(contact_text, self.styles['CustomNormal'])
            elements.append(contact_para)

        return elements

    def _build_estimate_details(self, estimate: Estimate):
        """Build estimate number, date, and status section"""
        elements = []

        # Estimate title
        title = Paragraph("ESTIMATE", self.styles['EstimateTitle'])
        elements.append(title)

        # Create table for estimate details
        details_data = [
            ['Estimate Number:', estimate.estimate_number],
            ['Estimate Date:', estimate.date],
            ['Due Date:', estimate.due_date or 'N/A'],
            ['Status:', estimate.status.title()]
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

    def _build_customer_details(self, estimate: Estimate):
        """Build customer information section"""
        elements = []

        # Section header
        header = Paragraph("Bill To:", self.styles['SectionHeader'])
        elements.append(header)

        # Customer details
        customer_lines = [estimate.customer_name]
        if estimate.customer_address:
            customer_lines.append(estimate.customer_address)
        if estimate.customer_email:
            customer_lines.append(f"Email: {estimate.customer_email}")
        if estimate.customer_gstin:
            customer_lines.append(f"GSTIN: {estimate.customer_gstin}")

        customer_text = "<br/>".join(customer_lines)
        customer_para = Paragraph(customer_text, self.styles['CustomNormal'])
        elements.append(customer_para)

        return elements

    def _build_items_table(self, estimate: Estimate):
        """Build the items table"""
        elements = []

        # Table headers
        headers = ['Description', 'Qty', 'Rate', 'Discount%', 'Amount']
        table_data = [headers]

        # Add items
        for item in estimate.items:
            # Wrap long item names in Paragraph for text wrapping
            item_name_para = Paragraph(item.name, self.styles['CustomNormal'])
            row = [
                item_name_para,
                f"{item.quantity:,.2f}",
                self._format_currency(item.unit_price),
                f"{item.discount_rate:,.1f}%",
                self._format_currency(item.line_total)
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
            ('FONTNAME', (0, 0), (-1, 0), self.unicode_font + '-Bold' if self.unicode_font == 'Helvetica' else self.unicode_font),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), self.unicode_font),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]

        # Alternate row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgrey))

        items_table.setStyle(TableStyle(table_style))
        elements.append(items_table)

        return elements

    def _build_totals_section(self, estimate: Estimate):
        """Build the totals section"""
        elements = []

        # Totals data
        totals_data = []

        # Subtotal
        totals_data.append(['Subtotal:', self._format_currency(estimate.subtotal)])

        # Global discount if applicable
        if estimate.global_discount_amount > 0:
            totals_data.append([
                f'Discount ({estimate.global_discount_rate:,.1f}%):',
                f"-{self._format_currency(estimate.global_discount_amount)}"
            ])

        # Tax
        if estimate.total_tax > 0:
            totals_data.append(['Tax:', self._format_currency(estimate.total_tax)])

        # Grand total
        totals_data.append(['Total:', self._format_currency(estimate.grand_total)])

        # Create totals table
        totals_table = Table(totals_data, colWidths=[4*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -2), self.unicode_font),
            ('FONTNAME', (1, 0), (1, -2), self.unicode_font),
            ('FONTNAME', (0, -1), (-1, -1), self.unicode_font + '-Bold' if self.unicode_font == 'Helvetica' else self.unicode_font),
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.darkblue),
        ]))

        elements.append(totals_table)
        return elements

    def _build_footer(self, estimate: Estimate):
        """Build footer with terms and notes"""
        elements = []

        # Notes
        if estimate.notes:
            notes_header = Paragraph("Notes:", self.styles['SectionHeader'])
            elements.append(notes_header)
            notes_para = Paragraph(estimate.notes, self.styles['CustomNormal'])
            elements.append(notes_para)
            elements.append(Spacer(1, 12))

        # Terms and conditions
        if estimate.terms or self.business_settings.terms_and_conditions:
            terms_text = estimate.terms or self.business_settings.terms_and_conditions
            terms_header = Paragraph("Terms & Conditions:", self.styles['SectionHeader'])
            elements.append(terms_header)
            terms_para = Paragraph(terms_text, self.styles['CustomNormal'])
            elements.append(terms_para)
            elements.append(Spacer(1, 12))

        # Footer message
        if self.business_settings.notes_footer:
            footer_para = Paragraph(
                self.business_settings.notes_footer,
                self.styles['CustomNormal']
            )
            elements.append(footer_para)

        return elements