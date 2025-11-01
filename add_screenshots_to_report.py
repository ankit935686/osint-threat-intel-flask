#!/usr/bin/env python3
"""
Helper script to add dashboard screenshots to the PDF report
Place your screenshot images in a 'screenshots' folder and run this script
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from datetime import datetime
import os
import glob

def add_screenshot_section(elements, h2_style, body_style, screenshot_folder="screenshots"):
    """
    Add dashboard screenshots to the report
    
    Args:
        elements: List of reportlab elements
        h2_style: Heading 2 style
        body_style: Body text style
        screenshot_folder: Folder containing screenshot images
    """
    
    # Check if screenshot folder exists
    if not os.path.exists(screenshot_folder):
        print(f"⚠ Warning: {screenshot_folder} folder not found")
        print(f"   Create a '{screenshot_folder}' folder and add your dashboard images")
        return elements
    
    # Find all image files in the screenshots folder
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']
    screenshot_files = []
    for ext in image_extensions:
        screenshot_files.extend(glob.glob(os.path.join(screenshot_folder, ext)))
    
    if not screenshot_files:
        print(f"⚠ Warning: No images found in {screenshot_folder} folder")
        print(f"   Add PNG or JPG images of your dashboard")
        return elements
    
    # Sort files alphabetically
    screenshot_files.sort()
    
    print(f"✓ Found {len(screenshot_files)} screenshot(s)")
    
    elements.append(Paragraph("4.3. Dashboard Screenshots", h2_style))
    
    intro_text = """
    The following screenshots demonstrate the live threat intelligence dashboard in action, 
    showcasing various visualizations and analytical views provided by the system.
    """
    elements.append(Paragraph(intro_text, body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Add each screenshot
    for idx, screenshot_path in enumerate(screenshot_files, 1):
        try:
            # Get filename without extension for caption
            filename = os.path.basename(screenshot_path)
            caption = filename.replace('_', ' ').replace('-', ' ').rsplit('.', 1)[0]
            
            # Add caption
            caption_style = ParagraphStyle(
                'Caption',
                parent=body_style,
                fontSize=9,
                fontName='Helvetica-Bold',
                spaceAfter=6
            )
            elements.append(Paragraph(f"Figure {idx}: {caption.title()}", caption_style))
            
            # Add image (resize to fit page width)
            img = Image(screenshot_path)
            
            # Calculate aspect ratio and resize
            available_width = 6.5 * inch  # Leave margins
            available_height = 4.5 * inch  # Reasonable height
            
            aspect = img.imageHeight / float(img.imageWidth)
            
            if img.imageWidth > available_width:
                img.drawWidth = available_width
                img.drawHeight = available_width * aspect
            else:
                img.drawWidth = img.imageWidth
                img.drawHeight = img.imageHeight
            
            # If height is still too large, scale down further
            if img.drawHeight > available_height:
                img.drawHeight = available_height
                img.drawWidth = available_height / aspect
            
            elements.append(img)
            elements.append(Spacer(1, 0.3*inch))
            
            print(f"  ✓ Added: {filename}")
            
        except Exception as e:
            print(f"  ✗ Failed to add {filename}: {str(e)}")
            continue
    
    return elements


def generate_report_with_screenshots(output_filename="Project_Report_OSINT_With_Screenshots.pdf"):
    """
    Generate the complete PDF report including screenshots
    """
    from generate_project_report import ProjectReportGenerator
    
    print("🚀 Generating PDF Report with Dashboard Screenshots")
    print("=" * 60)
    
    # Create custom generator that includes screenshots
    generator = ProjectReportGenerator()
    
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles (same as main generator)
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        fontName='Helvetica'
    )
    
    # Build report sections (reuse generator methods)
    story.extend(generator.create_title_page(title_style, body_style))
    story.append(PageBreak())
    
    story.extend(generator.create_abstract(heading1_style, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.extend(generator.create_system_architecture(heading1_style, heading2_style, body_style))
    story.append(PageBreak())
    
    story.extend(generator.create_module_collection(heading1_style, heading2_style, body_style))
    story.append(PageBreak())
    
    story.extend(generator.create_module_normalization(heading1_style, heading2_style, body_style))
    story.extend(generator.create_module_enrichment(heading1_style, heading2_style, body_style))
    story.append(PageBreak())
    
    story.extend(generator.create_module_merge(heading1_style, heading2_style, body_style))
    story.extend(generator.create_module_correlation(heading1_style, heading2_style, body_style))
    story.append(PageBreak())
    
    story.extend(generator.create_module_scoring(heading1_style, heading2_style, body_style))
    story.extend(generator.create_module_reporting(heading1_style, heading2_style, body_style))
    story.append(PageBreak())
    
    story.extend(generator.create_module_orchestration(heading1_style, heading2_style, body_style))
    story.append(PageBreak())
    
    # Dashboard section - add intro text
    story.append(Paragraph("4. End-to-End Showcase: The Threat Intelligence Dashboard", heading1_style))
    
    dashboard_text = """
    This section demonstrates the pipeline's primary reporting artifact: the live dashboard. The dashboard 
    provides a holistic view of the threat intelligence collected and processed by the system.
    """
    story.append(Paragraph(dashboard_text, body_style))
    
    story.append(Paragraph("4.1. Dashboard Overview", heading2_style))
    
    overview_text = """
    The main dashboard provides a high-level summary of the current threat landscape, designed for 
    quick consumption by a SOC analyst. The dashboard is built using Flask (backend) and vanilla 
    JavaScript with Chart.js (frontend).<br/><br/>
    
    <b>Key Features:</b>
    <ul>
    <li><b>Real-time Data:</b> Displays the latest processed threat intelligence</li>
    <li><b>Interactive Visualizations:</b> Multiple chart types for different insights</li>
    <li><b>Source Attribution:</b> Shows which feeds contributed to the intelligence</li>
    <li><b>Risk-based Filtering:</b> Allows analysts to focus on high-priority threats</li>
    <li><b>Search Functionality:</b> Quick lookup of specific indicators</li>
    </ul>
    """
    story.append(Paragraph(overview_text, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Add screenshots here
    add_screenshot_section(story, heading2_style, body_style)
    
    story.append(PageBreak())
    
    # Continue with remaining sections
    story.extend(generator.create_technology_stack(heading1_style, heading2_style, body_style))
    story.extend(generator.create_conclusion(heading1_style, body_style))
    
    # Build PDF
    doc.build(story)
    print(f"\n✅ Report with screenshots generated: {output_filename}")
    return output_filename


def main():
    """Main function"""
    print("\n📸 Dashboard Screenshot Addition Tool")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Create a 'screenshots' folder in the project directory")
    print("2. Add your dashboard screenshot images (PNG/JPG)")
    print("3. Run this script to generate the report with images")
    print("\nTip: Name your files descriptively:")
    print("  - dashboard_overview.png")
    print("  - risk_distribution_chart.png")
    print("  - correlation_graph.png")
    print("  etc.")
    print()
    
    try:
        # Check if screenshots folder exists
        if not os.path.exists("screenshots"):
            print("📁 Creating 'screenshots' folder...")
            os.makedirs("screenshots")
            print("✓ Folder created!")
            print("\n⚠ Please add your dashboard screenshot images to the 'screenshots' folder")
            print("  Then run this script again.")
            return 0
        
        # Generate report with screenshots
        output_file = generate_report_with_screenshots()
        
        # Get file size
        file_size = os.path.getsize(output_file) / 1024  # KB
        print(f"\nFile size: {file_size:.2f} KB")
        print(f"\n✅ Complete! You can now open: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
