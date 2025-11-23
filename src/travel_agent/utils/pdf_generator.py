"""PDF generation utility for Travel Buddy responses."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor
from reportlab.platypus.flowables import HRFlowable
from io import BytesIO
import re
from datetime import datetime


def clean_markdown(text):
    """Remove markdown syntax for plain text rendering."""
    # Remove headers (keep text)
    text = re.sub(r'^#+\s+(.*)$', r'\1', text, flags=re.MULTILINE)
    # Remove bold/italic but keep text
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove code blocks
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)
    return text


def markdown_to_paragraphs(text, styles):
    """Convert markdown text to ReportLab Paragraph objects with better formatting."""
    paragraphs = []
    lines = text.split('\n')
    
    current_paragraph = []
    in_list = False
    list_items = []
    
    for i, line in enumerate(lines):
        original_line = line
        line = line.strip()
        
        # Handle horizontal rules
        if line.startswith('---') or line.startswith('***') or line.startswith('___'):
            if current_paragraph:
                paragraphs.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                current_paragraph = []
            paragraphs.append(Spacer(1, 0.1*inch))
            paragraphs.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=HexColor('#cccccc')))
            paragraphs.append(Spacer(1, 0.15*inch))
            in_list = False
            continue
        
        if not line:
            if current_paragraph:
                paragraphs.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                paragraphs.append(Spacer(1, 0.12*inch))
                current_paragraph = []
            if list_items:
                for item in list_items:
                    paragraphs.append(Paragraph(item, styles['Normal']))
                    paragraphs.append(Spacer(1, 0.06*inch))
                list_items = []
            in_list = False
            continue
        
        # Handle headers
        if line.startswith('#'):
            if current_paragraph:
                paragraphs.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                paragraphs.append(Spacer(1, 0.12*inch))
                current_paragraph = []
            if list_items:
                for item in list_items:
                    paragraphs.append(Paragraph(item, styles['Normal']))
                    paragraphs.append(Spacer(1, 0.06*inch))
                list_items = []
            
            level = len(line) - len(line.lstrip('#'))
            header_text = line.lstrip('#').strip()
            # Remove emojis from headers for cleaner PDF
            header_text = re.sub(r'[📝🔍✨✅🚀💬]', '', header_text).strip()
            
            if level == 1:
                paragraphs.append(Spacer(1, 0.25*inch))
                paragraphs.append(Paragraph(header_text, styles['Heading1']))
                paragraphs.append(Spacer(1, 0.15*inch))
            elif level == 2:
                paragraphs.append(Spacer(1, 0.2*inch))
                paragraphs.append(Paragraph(header_text, styles['Heading2']))
                paragraphs.append(Spacer(1, 0.12*inch))
            elif level == 3:
                paragraphs.append(Spacer(1, 0.15*inch))
                paragraphs.append(Paragraph(header_text, styles['Heading3']))
                paragraphs.append(Spacer(1, 0.1*inch))
            else:
                paragraphs.append(Spacer(1, 0.1*inch))
                paragraphs.append(Paragraph(header_text, styles['Heading4']))
                paragraphs.append(Spacer(1, 0.08*inch))
            in_list = False
            continue
        
        # Handle lists
        if line.startswith('- ') or line.startswith('* ') or re.match(r'^\d+\.\s', line):
            if current_paragraph:
                paragraphs.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                paragraphs.append(Spacer(1, 0.1*inch))
                current_paragraph = []
            
            # Extract list item text
            list_text = re.sub(r'^[-*]\s+', '', line)
            list_text = re.sub(r'^\d+\.\s+', '', list_text)
            list_text = clean_markdown(list_text)
            
            # Use bullet point
            bullet = "•" if line.startswith('- ') or line.startswith('* ') else f"{re.match(r'^(\d+)\.', line).group(1)}."
            list_items.append(f"<b>{bullet}</b> {list_text}")
            in_list = True
            continue
        
        # Regular paragraph
        if in_list and list_items:
            for item in list_items:
                paragraphs.append(Paragraph(item, styles['Normal']))
                paragraphs.append(Spacer(1, 0.06*inch))
            list_items = []
            in_list = False
            paragraphs.append(Spacer(1, 0.08*inch))
        
        # Clean and add line
        cleaned_line = clean_markdown(line)
        if cleaned_line:
            current_paragraph.append(cleaned_line)
    
    # Add remaining content
    if current_paragraph:
        paragraphs.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
        paragraphs.append(Spacer(1, 0.12*inch))
    
    if list_items:
        for item in list_items:
            paragraphs.append(Paragraph(item, styles['Normal']))
            paragraphs.append(Spacer(1, 0.06*inch))
    
    return paragraphs


def generate_pdf(content, title="Travel Plan"):
    """Generate PDF from markdown content with professional formatting."""
    buffer = BytesIO()
    
    # Create PDF document with better margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=60,
        leftMargin=60,
        topMargin=80,
        bottomMargin=60
    )
    
    # Create styles
    styles = getSampleStyleSheet()
    
    # Custom title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=HexColor('#1f77b4'),
        spaceAfter=15,
        spaceBefore=0,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Custom subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#666666'),
        spaceAfter=25,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    # Custom heading styles
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=HexColor('#1f77b4'),
        spaceAfter=14,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderPadding=5,
        borderColor=HexColor('#e0e0e0'),
        borderWidth=0,
        leftIndent=0
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=16,
        fontName='Helvetica-Bold'
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Enhanced normal style
    normal_style = ParagraphStyle(
        'EnhancedNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#333333'),
        spaceAfter=8,
        leading=14,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    # Build content
    story = []
    
    # Title section with better formatting
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Travel Buddy", title_style))
    story.append(Paragraph(title, ParagraphStyle(
        'DocTitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=HexColor('#2c3e50'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        subtitle_style
    ))
    story.append(Spacer(1, 0.4*inch))
    story.append(HRFlowable(width="100%", thickness=2, lineCap='round', color=HexColor('#1f77b4')))
    story.append(Spacer(1, 0.3*inch))
    
    # Add content with enhanced formatting
    content_paragraphs = markdown_to_paragraphs(content, {
        'Normal': normal_style,
        'Heading1': heading1_style,
        'Heading2': heading2_style,
        'Heading3': heading3_style,
        'Heading4': styles['Heading4']
    })
    
    story.extend(content_paragraphs)
    
    # Add footer space
    story.append(Spacer(1, 0.3*inch))
    story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=HexColor('#cccccc')))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "<i>Generated by Travel Buddy - Powered by Gemini LLM</i>",
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=HexColor('#999999'),
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
    ))
    
    # Build PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer


def create_download_pdf(content, filename="travel_plan.pdf"):
    """Create a downloadable PDF file."""
    pdf_buffer = generate_pdf(content, "Travel Plan")
    return pdf_buffer.getvalue()

