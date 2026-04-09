"""
Report Generator Module
Exports analysis into a professional PDF format including Plotly charts.
"""
from fpdf import FPDF
import io
import os
import urllib.request

def ensure_fonts():
    """Ensure Thai-compatible fonts are available."""
    font_dir = "fonts"
    if not os.path.exists(font_dir):
        os.makedirs(font_dir)
        
    regular = os.path.join(font_dir, "Sarabun-Regular.ttf")
    bold = os.path.join(font_dir, "Sarabun-Bold.ttf")
    
    if not os.path.exists(regular):
        urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf", regular)
    if not os.path.exists(bold):
        urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf", bold)
        
    return regular, bold

class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        regular, bold = ensure_fonts()
        self.add_font('Sarabun', '', regular)
        self.add_font('Sarabun', 'B', bold)

    def header(self):
        self.set_fill_color(13, 17, 23)
        self.rect(0, 0, 210, 30, 'F')
        self.set_y(10)
        self.set_text_color(0, 229, 255)
        self.set_font('Sarabun', 'B', 20)
        self.cell(0, 10, 'Satellite Conjunction Analysis Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Sarabun', '', 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(sat1_name, sat2_name, max_pc, risk_level, distance_km, tca_time, fig_dist, fig_heatmap, fig_3d, fig_earth):
    """
    Generate a byte string of the PDF containing all analysis details.
    Uses kaleido under the hood via plotly's write_image.
    """
    pdf = PDF()
    pdf.add_page()
    
    # Overview
    pdf.set_y(35)
    pdf.set_font('Sarabun', 'B', 16)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, f'Encounter: {sat1_name} vs {sat2_name}', ln=True)
    
    pdf.set_font('Sarabun', '', 12)
    pdf.cell(0, 8, f'Time of Closest Approach (TCA): {tca_time}', ln=True)
    pdf.cell(0, 8, f'Minimum Distance: {distance_km:.3f} km', ln=True)
    pdf.cell(0, 8, f'Max Collision Probability: {max_pc:.4e}', ln=True)
    
    # Risk Level
    pdf.set_font('Sarabun', 'B', 14)
    if "CRITICAL" in risk_level.upper() or "วิกฤต" in risk_level:
        pdf.set_text_color(255, 0, 0)
    elif "WARNING" in risk_level.upper() or "เตือน" in risk_level:
        pdf.set_text_color(255, 165, 0)
    else:
        pdf.set_text_color(0, 200, 0)
    pdf.cell(0, 10, f'ASSESSED RISK: {risk_level}', ln=True)
    
    # Image Paths
    dist_path = "temp_dist.png"
    heatmap_path = "temp_heatmap.png"
    ric_path = "temp_ric.png"
    earth_path = "temp_earth.png"
    
    try:
        # Save temp images via Kaleido
        fig_dist.write_image(dist_path, scale=1.5)
        fig_heatmap.write_image(heatmap_path, scale=1.5)
        fig_3d.write_image(ric_path, scale=1.5)
        fig_earth.write_image(earth_path, scale=1.5)
        
        pdf.set_y(85)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Sarabun', 'B', 14)
        pdf.cell(0, 10, 'Distance Over Time', ln=True)
        pdf.image(dist_path, w=180)
        
        pdf.add_page()
        pdf.set_font('Sarabun', 'B', 14)
        pdf.cell(0, 10, 'Collision Probability Heatmap', ln=True)
        pdf.image(heatmap_path, w=180)
        
        pdf.cell(0, 10, '3D Relative Orbit (RIC)', ln=True)
        pdf.image(ric_path, w=180)
        
        pdf.add_page()
        pdf.set_font('Sarabun', 'B', 14)
        pdf.cell(0, 10, '3D Earth Orbit View (ITRF)', ln=True)
        pdf.image(earth_path, w=180)
    except Exception as e:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, f'Error generating charts in PDF: {e}', ln=True)
    finally:
        # Cleanup
        for path in [dist_path, heatmap_path, ric_path, earth_path]:
            if os.path.exists(path):
                os.remove(path)
                
    return bytes(pdf.output())
