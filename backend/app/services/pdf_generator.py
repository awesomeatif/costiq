"""
PDF Report Generator Service

Generates CFO-ready Cost Optimization Diagnostic PDF reports.
Uses ReportLab for professional PDF generation.
"""

from io import BytesIO
from datetime import datetime
from typing import List, Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.models.finding import Finding


# =============================================================================
# CFO-Friendly Language Mappings
# =============================================================================

CATEGORY_DISPLAY = {
    "price_variance": "Vendor Price Optimization",
    "contract_mismatch": "Contract Compliance Gap",
    "overstock": "Inventory Capital Efficiency",
    "expiry_risk": "Inventory Wastage Prevention"
}

SEVERITY_DISPLAY = {
    "high": "Immediate Action Required",
    "medium": "Action Recommended",
    "low": "Optimize When Feasible"
}

CATEGORY_ACTIONS = {
    "price_variance": "Consolidate procurement to lowest-cost vendors or renegotiate pricing",
    "contract_mismatch": "Audit invoices against contract terms and pursue credits",
    "overstock": "Reduce order quantities and implement demand-based ordering",
    "expiry_risk": "Expedite usage, redistribute, or arrange vendor returns"
}


# =============================================================================
# Custom Styles
# =============================================================================

def get_custom_styles():
    """Create professional styles for the report."""
    styles = getSampleStyleSheet()
    
    # Title style
    styles.add(ParagraphStyle(
        name='ReportTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a365d')
    ))
    
    # Section heading
    styles.add(ParagraphStyle(
        name='SectionHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor('#2c5282')
    ))
    
    # Subsection
    styles.add(ParagraphStyle(
        name='SubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.HexColor('#2d3748')
    ))
    
    # Body text (using CustomBody to avoid conflict)
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        leading=14
    ))
    
    # Key metric
    styles.add(ParagraphStyle(
        name='KeyMetric',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        textColor=colors.HexColor('#c53030')
    ))
    
    # Footer
    styles.add(ParagraphStyle(
        name='CustomFooter',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
        alignment=TA_CENTER
    ))
    
    return styles


# =============================================================================
# PDF Generator Class
# =============================================================================

class CostIQReportGenerator:
    """
    Generates professional Cost Optimization Diagnostic PDF.
    
    Sections:
    1. Executive Summary
    2. Cost Leakage Overview
    3. Top Findings Detail
    4. Action Plan
    5. Methodology & Scope
    """
    
    def __init__(self, findings: List[Finding], org_name: str = "Your Hospital"):
        self.findings = findings
        self.org_name = org_name
        self.styles = get_custom_styles()
        self.report_date = datetime.now().strftime("%B %d, %Y")
        
        # Pre-calculate metrics
        self.total_findings = len(findings)
        self.total_savings = sum(f.potential_savings or 0 for f in findings)
        self.high_priority = len([f for f in findings if f.severity == "high"])
        self.by_category = self._group_by_category()
    
    def _group_by_category(self) -> Dict[str, List[Finding]]:
        """Group findings by category."""
        grouped = {}
        for f in self.findings:
            if f.category not in grouped:
                grouped[f.category] = []
            grouped[f.category].append(f)
        return grouped
    
    def generate(self) -> BytesIO:
        """Generate the complete PDF report."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Build all sections
        story.extend(self._build_cover())
        story.append(PageBreak())
        story.extend(self._build_executive_summary())
        story.append(PageBreak())
        story.extend(self._build_findings_overview())
        story.append(PageBreak())
        story.extend(self._build_top_findings())
        story.append(PageBreak())
        story.extend(self._build_action_plan())
        story.append(PageBreak())
        story.extend(self._build_methodology())
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _build_cover(self) -> List:
        """Build cover page."""
        elements = []
        
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(
            "COST OPTIMIZATION DIAGNOSTIC",
            self.styles['ReportTitle']
        ))
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(
            f"Prepared for: {self.org_name}",
            self.styles['SubHeading']
        ))
        elements.append(Paragraph(
            f"Report Date: {self.report_date}",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 1*inch))
        
        # Key metrics box
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2c5282')))
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(
            f"Identified Savings Opportunity: ${self.total_savings:,.2f}",
            self.styles['KeyMetric']
        ))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(
            f"{self.high_priority} High-Priority Issues Requiring Immediate Attention",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.3*inch))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2c5282')))
        
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(
            "CONFIDENTIAL - For Internal Use Only",
            self.styles['CustomFooter']
        ))
        elements.append(Paragraph(
            "Generated by CostIQ - Healthcare Cost Intelligence Platform",
            self.styles['CustomFooter']
        ))
        
        return elements
    
    def _build_executive_summary(self) -> List:
        """Build executive summary page."""
        elements = []
        
        elements.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.gray))
        elements.append(Spacer(1, 0.2*inch))
        
        # Key findings summary
        elements.append(Paragraph(
            f"Our analysis of your operational data has identified <b>${self.total_savings:,.2f}</b> "
            f"in potential cost savings across {self.total_findings} actionable findings.",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Summary metrics table
        summary_data = [
            ["Metric", "Value"],
            ["Total Findings Identified", str(self.total_findings)],
            ["High Priority Issues", str(self.high_priority)],
            ["Total Savings Opportunity", f"${self.total_savings:,.2f}"],
            ["Projected Annual Impact*", f"${self.total_savings * 4:,.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3.5*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(
            "*Annual impact assumes quarterly recurrence of identified patterns",
            self.styles['CustomFooter']
        ))
        
        # Breakdown by category
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("Savings by Category", self.styles['SubHeading']))
        
        category_data = [["Category", "Findings", "Potential Savings"]]
        for cat, findings in sorted(self.by_category.items()):
            cat_savings = sum(f.potential_savings or 0 for f in findings)
            category_data.append([
                CATEGORY_DISPLAY.get(cat, cat),
                str(len(findings)),
                f"${cat_savings:,.2f}"
            ])
        
        cat_table = Table(category_data, colWidths=[3*inch, 1.5*inch, 2*inch])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(cat_table)
        
        return elements
    
    def _build_findings_overview(self) -> List:
        """Build cost leakage overview table."""
        elements = []
        
        elements.append(Paragraph("COST LEAKAGE OVERVIEW", self.styles['SectionHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.gray))
        elements.append(Spacer(1, 0.2*inch))
        
        elements.append(Paragraph(
            "The following table summarizes all identified cost optimization opportunities, "
            "prioritized by potential financial impact.",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Findings table
        table_data = [["Priority", "Category", "Description", "Savings"]]
        
        # Sort by savings descending
        sorted_findings = sorted(
            self.findings,
            key=lambda f: f.potential_savings or 0,
            reverse=True
        )
        
        for f in sorted_findings[:15]:  # Top 15 to fit on page
            # Truncate description for table
            desc = f.description[:80] + "..." if len(f.description) > 80 else f.description
            table_data.append([
                SEVERITY_DISPLAY.get(f.severity, f.severity)[:10],
                CATEGORY_DISPLAY.get(f.category, f.category)[:20],
                desc,
                f"${f.potential_savings:,.0f}" if f.potential_savings else "-"
            ])
        
        findings_table = Table(
            table_data,
            colWidths=[1*inch, 1.3*inch, 3.2*inch, 0.8*inch]
        )
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        # Alternate row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                findings_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#edf2f7'))
                ]))
        
        elements.append(findings_table)
        
        if len(self.findings) > 15:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(
                f"Showing top 15 of {len(self.findings)} total findings",
                self.styles['CustomFooter']
            ))
        
        return elements
    
    def _build_top_findings(self) -> List:
        """Build detailed view of top findings."""
        elements = []
        
        elements.append(Paragraph("TOP PRIORITY FINDINGS", self.styles['SectionHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.gray))
        elements.append(Spacer(1, 0.2*inch))
        
        # Get top 5 by savings
        top_findings = sorted(
            self.findings,
            key=lambda f: f.potential_savings or 0,
            reverse=True
        )[:5]
        
        for i, f in enumerate(top_findings, 1):
            elements.append(Paragraph(
                f"Finding #{i}: {CATEGORY_DISPLAY.get(f.category, f.category)}",
                self.styles['SubHeading']
            ))
            
            # Details table
            details = [
                ["Priority Level:", SEVERITY_DISPLAY.get(f.severity, f.severity)],
                ["Potential Savings:", f"${f.potential_savings:,.2f}" if f.potential_savings else "TBD"],
                ["Description:", f.description],
                ["Recommended Action:", CATEGORY_ACTIONS.get(f.category, "Review and address")]
            ]
            
            detail_table = Table(details, colWidths=[1.5*inch, 5*inch])
            detail_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(detail_table)
            elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _build_action_plan(self) -> List:
        """Build action plan section."""
        elements = []
        
        elements.append(Paragraph("RECOMMENDED ACTION PLAN", self.styles['SectionHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.gray))
        elements.append(Spacer(1, 0.2*inch))
        
        elements.append(Paragraph(
            "Based on the identified findings, we recommend the following prioritized actions:",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Immediate actions (high severity)
        elements.append(Paragraph("Immediate Actions (Next 30 Days)", self.styles['SubHeading']))
        high_priority = [f for f in self.findings if f.severity == "high"]
        if high_priority:
            for i, cat in enumerate(set(f.category for f in high_priority), 1):
                cat_findings = [f for f in high_priority if f.category == cat]
                cat_savings = sum(f.potential_savings or 0 for f in cat_findings)
                elements.append(Paragraph(
                    f"{i}. <b>{CATEGORY_DISPLAY.get(cat, cat)}</b>: "
                    f"{CATEGORY_ACTIONS.get(cat, 'Address immediately')} "
                    f"(Est. savings: ${cat_savings:,.2f})",
                    self.styles['CustomBody']
                ))
        else:
            elements.append(Paragraph("No immediate actions required.", self.styles['CustomBody']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Short-term actions
        elements.append(Paragraph("Short-Term Actions (30-60 Days)", self.styles['SubHeading']))
        medium_priority = [f for f in self.findings if f.severity == "medium"]
        if medium_priority:
            for i, cat in enumerate(set(f.category for f in medium_priority), 1):
                cat_findings = [f for f in medium_priority if f.category == cat]
                cat_savings = sum(f.potential_savings or 0 for f in cat_findings)
                elements.append(Paragraph(
                    f"{i}. <b>{CATEGORY_DISPLAY.get(cat, cat)}</b>: "
                    f"{CATEGORY_ACTIONS.get(cat, 'Review and address')} "
                    f"(Est. savings: ${cat_savings:,.2f})",
                    self.styles['CustomBody']
                ))
        else:
            elements.append(Paragraph("No short-term actions identified.", self.styles['CustomBody']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary box
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#38a169')))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(
            f"<b>Total Addressable Savings: ${self.total_savings:,.2f}</b>",
            self.styles['CustomBody']
        ))
        elements.append(Paragraph(
            "Conservative estimate based on current data. Actual savings may vary based on "
            "implementation speed and negotiation outcomes.",
            self.styles['CustomFooter']
        ))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#38a169')))
        
        return elements
    
    def _build_methodology(self) -> List:
        """Build methodology and scope section."""
        elements = []
        
        elements.append(Paragraph("METHODOLOGY & SCOPE", self.styles['SectionHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.gray))
        elements.append(Spacer(1, 0.2*inch))
        
        elements.append(Paragraph("Analysis Approach", self.styles['SubHeading']))
        elements.append(Paragraph(
            "This diagnostic was conducted using rule-based analysis of your operational data. "
            "The following categories were evaluated:",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.1*inch))
        
        methodology_items = [
            "<b>Vendor Price Variance</b>: Comparison of unit prices across vendors for identical items (SKUs) to identify pricing inconsistencies.",
            "<b>Contract Compliance</b>: Validation of invoiced prices against contracted rates to identify overcharges.",
            "<b>Inventory Efficiency</b>: Analysis of stock levels relative to usage rates to identify capital tied up in excess inventory.",
            "<b>Expiration Risk</b>: Identification of items approaching expiration with significant quantities remaining."
        ]
        
        for item in methodology_items:
            elements.append(Paragraph(f"• {item}", self.styles['CustomBody']))
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("Data Scope", self.styles['SubHeading']))
        elements.append(Paragraph(
            f"This analysis was based on data uploaded to CostIQ as of {self.report_date}. "
            "Findings reflect point-in-time analysis and should be validated with current operational data "
            "before taking action.",
            self.styles['CustomBody']
        ))
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("Limitations", self.styles['SubHeading']))
        elements.append(Paragraph(
            "• Savings estimates are projections based on available data and may vary with implementation<br/>"
            "• Analysis limited to categories with sufficient data for comparison<br/>"
            "• Contract pricing comparisons require contract data to be present in uploaded files<br/>"
            "• Expiration analysis depends on expiry dates being populated in inventory records",
            self.styles['CustomBody']
        ))
        
        elements.append(Spacer(1, 0.5*inch))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.gray))
        elements.append(Paragraph(
            f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | CostIQ v1.0",
            self.styles['CustomFooter']
        ))
        
        return elements


def generate_report(findings: List[Finding], org_name: str = "Your Hospital") -> BytesIO:
    """
    Main entry point for PDF generation.
    
    Args:
        findings: List of Finding objects from database
        org_name: Organization name for the report
        
    Returns:
        BytesIO buffer containing the PDF
    """
    generator = CostIQReportGenerator(findings, org_name)
    return generator.generate()

