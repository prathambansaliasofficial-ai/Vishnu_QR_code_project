from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

# Configuration
qr_folder = "vishnu_qrcodes"
output_pdf = "vishnu_qr_sheets.pdf"
images_per_page = 12  # 3 columns x 4 rows
cols = 3
rows = 4

# Get list of all images
image_files = [f for f in os.listdir(qr_folder) if f.endswith('.png')]
image_files.sort() # Keep them in alphabetical/numeric order

# Setup PDF
c = canvas.Canvas(output_pdf, pagesize=A4)
width, height = A4

# Calculate grid dimensions (assuming A4 margins)
margin = 40
cell_width = (width - 2 * margin) / cols
cell_height = (height - 2 * margin) / rows

for i, img_file in enumerate(image_files):
    # If we finished a page, start a new one
    if i > 0 and i % images_per_page == 0:
        c.showPage()
    
    # Calculate position
    col = i % cols
    row = (i // cols) % rows
    
    # Invert row because PDF coordinates start from bottom-left
    y_pos = height - margin - (row + 1) * cell_height
    x_pos = margin + col * cell_width
    
    # Draw image
    img_path = os.path.join(qr_folder, img_file)
    c.drawImage(img_path, x_pos + 10, y_pos + 10, width=cell_width-20, height=cell_height-20, preserveAspectRatio=True)

c.save()
print(f"Success! '{output_pdf}' is ready to print with {len(image_files)} QR codes.")