import os
import smtplib
from email.message import EmailMessage
from icalendar import Calendar, Event
from datetime import datetime
from email.utils import formataddr
from zoneinfo import ZoneInfo

SMTP_HOST     = os.getenv("SMTP_HOST")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
SMTP_USER     = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM     = os.getenv("SMTP_FROM")

def format_slot(start_dt: datetime, end_dt: datetime) -> str:
  # e.g. "Tuesday, 12 May 2025, 10:00 AM – 10:30 AM AEST"
  # Ensure both datetimes are in AEST
  tz = ZoneInfo("Australia/Melbourne")
  start_local = start_dt.astimezone(tz)
  end_local   = end_dt.astimezone(tz)

  # Format components
  date_str  = start_local.strftime("%A, %d %B %Y")
  start_str = start_local.strftime("%I:%M %p")
  end_str   = end_local.strftime("%I:%M %p")
  tz_name = start_local.tzname() or "AEST"

  return f"{date_str}, {start_str} – {end_str} {tz_name}"

def send_appointment_email(
  to_email: str,
  appt: dict
):
  # build the ICS calendar invite
  cal = Calendar()
  cal.add('prodid', '-//Smart Scheduler//')
  cal.add('version', '2.0')

  ev = Event()
  ev.add('summary', f"Your doctor's appointment with {appt['provider_name']}")
  start_dt = (
    appt['start']
    if isinstance(appt['start'], datetime)
    else datetime.fromisoformat(appt['start'])
  )
  end_dt = (
    appt['end']
    if isinstance(appt['end'], datetime)
    else datetime.fromisoformat(appt['end'])
  )
  ev.add('dtstart', start_dt)
  ev.add('dtend', end_dt)
  ev.add('description', appt.get('notes', ''))
  cal.add_component(ev)

  ics_bytes = cal.to_ical()

  # email 
  msg = EmailMessage()
  msg['Subject'] = "Your Appointment Confirmation"
  display_name = "Smart Scheduler Admin"
  msg['From'] = formataddr((display_name, SMTP_FROM))
  # msg['From']    = SMTP_FROM
  msg['To']      = to_email
  readable_time = format_slot(start_dt, end_dt)
  msg.set_content(
    f"""
      Hello {appt['patient']['name']},\n\n"
      Your appointment has been confirmed for {readable_time}.
      Please find the calendar invitation attached.\n\n
      Thank you!
    """
  )
  # styled HTML version
  html = f"""
<html>
  <body style="font-family: Arial, sans-serif; color: #333; padding: 2em; background-color: white;">
    <div style="border: 1px solid #ddd">
      <div style="background-color: #8c00c8; padding: 0.5em 2em;">
        <h2 style="color: #ffffff;">Appointment Confirmed!</h2>
      </div>
      <div style="padding: 1em 2em;">
        <p>Hi <strong>{appt['patient']['name']}</strong>,</p>
        <p>Your appointment with <strong>{appt['provider_name']}</strong> is set for:</p>
        <table cellpadding="5" cellspacing="0" style="border: 1px solid #ddd; width: 90%;">
          <tr>
            <td style="background: #f3d8fec1; padding: 0.5em 0.7em; text-align: left;">When:</td>
            <td style="text-align: left; padding: 0.5em 0.7em;">{readable_time}</td>
          </tr>
          <tr>
            <td style="background: #f3d8fec1; padding: 0.5em 0.7em; text-align: left;">Notes:</td>
            <td style="text-align: left; padding: 0.5em 0.7em;">{appt.get('notes','None')}</td>
          </tr>
        </table>
        <p style="margin-top: 2.5em; margin-bottom: 1em;">Download the attached <code>.ics</code> file to add it to your calendar.</p>
        <hr />
        <p style="font-size:0.8em;color:#8c00c8c1;">
          If you have any questions, just reply to this email.
        </p>
      </div>
    </div>
  </body>
</html>
"""
  
  msg.add_alternative(html, subtype='html')
  msg.add_attachment(
    ics_bytes,
    maintype='text',
    subtype='calendar',
    filename='appointment.ics'
  )

  # send via SMTP
  with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
    smtp.starttls()
    smtp.login(SMTP_USER, SMTP_PASSWORD)
    smtp.send_message(msg)
