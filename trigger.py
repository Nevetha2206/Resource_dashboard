# SENDER_EMAIL = "anshuchowdaryalap53@gmail.com"
# SENDER_PASSWORD = "icce wlov vbwf ffym"   # e.g., Gmail App Password
# RECEIVER_EMAILS = ["alapatidevianusha@gmail.com"]

import smtplib
import schedule
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import pandas as pd
from io import BytesIO

# Import from your app
from app import generate_critical_report_pdf, load_excel, EXCEL_PATH

# ---------------- Email Config ----------------
SENDER_EMAIL = "neve.nevetha123@gmail.com"
SENDER_PASSWORD = "fsln outh pvgn aceu"   # e.g., Gmail App Password
RECEIVER_EMAILS = ["neve.nevetha123@gmail.com"]  # Add multiple emails if needed

# ---------------- Job to Run Daily ----------------
def send_daily_report():
    print(f"📅 Generating report at {datetime.now()}")

    resource_df, so_df, emp_df, *_ = load_excel(EXCEL_PATH)
    if resource_df.empty:
        print("⚠️ No data found!")
        return

    # --- Use the same criteria as Tab 4 for critical records ---
    now = pd.Timestamp.now()
    end_of_current_month = (
        now.replace(day=1) + pd.offsets.MonthEnd(0)
    ).normalize() + pd.Timedelta(hours=23, minutes=59, seconds=59)

    cutoff_condition = (
        resource_df.get('fulfilmentDateCutoff', pd.Series(dtype='datetime64[ns]')).notna()
        & (pd.to_datetime(resource_df['fulfilmentDateCutoff'], errors='coerce') <= end_of_current_month)
    )
    rev_loss_condition = resource_df['revLoss'].astype(str).str.upper().isin(['Y', 'YES'])
    delivery_risk_condition = resource_df['deliveryRisk'].astype(str).str.lower().isin(['yes', 'y', 'true'])
    priority_condition = resource_df['priority'].astype(str).str.lower().eq('high')

    combined_condition = cutoff_condition | rev_loss_condition | delivery_risk_condition & priority_condition
    critical_df = resource_df[combined_condition]

    if critical_df.empty:
        print("✅ No critical requirements today.")
        return

    # Generate the same PDF as Tab 4
    pdf_data = generate_critical_report_pdf(critical_df)

    # ---------- Email Setup ----------
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECEIVER_EMAILS)
    msg["Subject"] = f"Daily Critical Resource Report - {datetime.now():%Y-%m-%d}"
    msg.attach(MIMEText("Attached is today's Critical Resource Report PDF from the dashboard.", "plain"))

    # Attach PDF
    attachment = MIMEApplication(pdf_data, _subtype="pdf")
    attachment.add_header("Content-Disposition", "attachment", filename="Critical_Resource_Report.pdf")
    msg.attach(attachment)

    # Send email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", e)

# ---------------- Scheduler ----------------
# Change time as needed (24-hour format)
schedule.every().day.at("15:10").do(send_daily_report)

print("⏰ Scheduler started... waiting for next run.")
while True:
    schedule.run_pending()
    time.sleep(60)
