from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def export_schedule_to_pdf(schedule_data, filename="timetable.pdf"):
    """
    Exports a given schedule to a PDF file.
    schedule_data should be a list of lists, formatted for the table.
    """
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []

    # Example data format:
    # data = [
    #     ['Time', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
    #     ['09:00-10:00', 'Math (Mr. S)', 'Physics (Dr. E)', '', 'History (Mrs. J)', ''],
    #     ...
    # ]

    # Create Table Style
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey), # Header row
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    # Create Table
    table = Table(schedule_data)
    table.setStyle(style)

    elements.append(table)
    doc.build(elements)
    print(f"PDF exported to {filename}")

if __name__ == '__main__':
  # Sample data for demonstration
  sample_data = [
  ['Time Slot', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
  ['09:00-10:00', 'Math\nMr. Smith\nRoom 101', 'History\nMrs. Jones\nRoom 102', '', '', 'Physics\nMr. Smith\nLab A'],
  ['10:00-11:00', '', 'Math\nMr. Smith\nRoom 101', '', 'History\nMrs. Jones\nRoom 102', ''],
  ['11:00-12:00', 'Physics\nMr. Smith\nLab A', '', 'Math\nMr. Smith\nRoom 101', '', ''],
  ]
  export_schedule_to_pdf(sample_data, "class_9a_timetable.pdf")