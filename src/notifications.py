"""
Prometheus V7.3 - Notification System
Email notifications and PDF reports for DreamLeague matches.
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz
from io import BytesIO

# Recipients
RECIPIENTS = [
    "moises.costa12345@gmail.com",
    "gabrielol2035@gmail.com"
]

# Timezone
SP_TZ = pytz.timezone('America/Sao_Paulo')


def get_hours_until_match(match_time: datetime) -> float:
    """Calculate hours until match starts."""
    now = datetime.now(SP_TZ)
    if match_time.tzinfo is None:
        match_time = SP_TZ.localize(match_time)
    delta = match_time - now
    return delta.total_seconds() / 3600


def format_countdown(hours: float) -> str:
    """Format countdown string."""
    if hours < 0:
        return "🔴 LIVE ou Finalizada"
    elif hours < 1:
        minutes = int(hours * 60)
        return f"⏰ {minutes}min"
    elif hours < 24:
        h = int(hours)
        m = int((hours - h) * 60)
        return f"⏰ {h}h {m}min"
    else:
        days = int(hours / 24)
        remaining_hours = int(hours % 24)
        return f"📅 {days}d {remaining_hours}h"


def get_countdown_color(hours: float) -> str:
    """Get color based on time remaining."""
    if hours < 0:
        return "🔴"  # Live/finished
    elif hours < 2:
        return "🟠"  # Very soon
    elif hours < 6:
        return "🟡"  # Today
    elif hours < 24:
        return "🟢"  # Within 24h
    else:
        return "⚪"  # Future


class MatchSchedule:
    """DreamLeague S27 match schedule with countdown."""
    
    # DreamLeague S27 Schedule (Group Stage - December 2024)
    SCHEDULE = [
        # Day 1 - December 10
        {"date": "2024-12-10", "time": "10:00", "team_a": "Team Liquid", "team_b": "Tundra Esports", "format": "Bo2"},
        {"date": "2024-12-10", "time": "13:00", "team_a": "Gaimin Gladiators", "team_b": "BetBoom Team", "format": "Bo2"},
        {"date": "2024-12-10", "time": "16:00", "team_a": "Team Falcons", "team_b": "Aurora", "format": "Bo2"},
        # Day 2 - December 11
        {"date": "2024-12-11", "time": "10:00", "team_a": "Team Spirit", "team_b": "NAVI", "format": "Bo2"},
        {"date": "2024-12-11", "time": "13:00", "team_a": "OG", "team_b": "1WIN", "format": "Bo2"},
        {"date": "2024-12-11", "time": "16:00", "team_a": "Team Liquid", "team_b": "Gaimin Gladiators", "format": "Bo2"},
        # Day 3 - December 12
        {"date": "2024-12-12", "time": "10:00", "team_a": "Tundra Esports", "team_b": "BetBoom Team", "format": "Bo2"},
        {"date": "2024-12-12", "time": "13:00", "team_a": "Team Falcons", "team_b": "Team Spirit", "format": "Bo2"},
        {"date": "2024-12-12", "time": "16:00", "team_a": "Aurora", "team_b": "NAVI", "format": "Bo2"},
        # Add more matches as needed...
    ]
    
    @classmethod
    def get_upcoming_matches(cls, hours_ahead: int = 48) -> List[Dict]:
        """Get matches within the next N hours."""
        now = datetime.now(SP_TZ)
        cutoff = now + timedelta(hours=hours_ahead)
        
        upcoming = []
        for match in cls.SCHEDULE:
            match_dt = datetime.strptime(f"{match['date']} {match['time']}", "%Y-%m-%d %H:%M")
            match_dt = SP_TZ.localize(match_dt)
            
            if now <= match_dt <= cutoff:
                hours = get_hours_until_match(match_dt)
                upcoming.append({
                    **match,
                    "datetime": match_dt,
                    "hours_until": hours,
                    "countdown": format_countdown(hours),
                    "countdown_color": get_countdown_color(hours)
                })
        
        return sorted(upcoming, key=lambda x: x["datetime"])
    
    @classmethod
    def get_todays_matches(cls) -> List[Dict]:
        """Get all matches for today."""
        today = datetime.now(SP_TZ).strftime("%Y-%m-%d")
        
        todays = []
        for match in cls.SCHEDULE:
            if match["date"] == today:
                match_dt = datetime.strptime(f"{match['date']} {match['time']}", "%Y-%m-%d %H:%M")
                match_dt = SP_TZ.localize(match_dt)
                hours = get_hours_until_match(match_dt)
                todays.append({
                    **match,
                    "datetime": match_dt,
                    "hours_until": hours,
                    "countdown": format_countdown(hours),
                    "countdown_color": get_countdown_color(hours)
                })
        
        return sorted(todays, key=lambda x: x["datetime"])
    
    @classmethod
    def get_matches_needing_report(cls, hours_before: float = 2.0) -> List[Dict]:
        """Get matches that need PDF report (within 2 hours)."""
        now = datetime.now(SP_TZ)
        
        needing_report = []
        for match in cls.SCHEDULE:
            match_dt = datetime.strptime(f"{match['date']} {match['time']}", "%Y-%m-%d %H:%M")
            match_dt = SP_TZ.localize(match_dt)
            
            hours = get_hours_until_match(match_dt)
            if 0 < hours <= hours_before:
                needing_report.append({
                    **match,
                    "datetime": match_dt,
                    "hours_until": hours,
                    "countdown": format_countdown(hours)
                })
        
        return needing_report


class EmailNotifier:
    """Email notification system."""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
    
    def send_email(
        self, 
        to_emails: List[str],
        subject: str,
        body_html: str,
        attachments: List[Dict] = None
    ) -> bool:
        """Send email with optional attachments."""
        if not self.smtp_user or not self.smtp_password:
            print("⚠️ SMTP credentials not configured")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ", ".join(to_emails)
            msg['Subject'] = subject
            
            # HTML body
            msg.attach(MIMEText(body_html, 'html'))
            
            # Attachments
            if attachments:
                for att in attachments:
                    part = MIMEApplication(att['data'], Name=att['filename'])
                    part['Content-Disposition'] = f'attachment; filename="{att["filename"]}"'
                    msg.attach(part)
            
            # Send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {to_emails}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def send_daily_schedule(self, to_emails: List[str] = None) -> bool:
        """Send daily match schedule email."""
        if to_emails is None:
            to_emails = RECIPIENTS
        
        matches = MatchSchedule.get_todays_matches()
        
        if not matches:
            return False
        
        today = datetime.now(SP_TZ).strftime("%d/%m/%Y")
        
        # Build HTML
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; text-align: center; }}
                .match {{ background: #16213e; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #667eea; }}
                .time {{ color: #ffd700; font-weight: bold; font-size: 18px; }}
                .teams {{ font-size: 16px; margin: 10px 0; }}
                .format {{ color: #888; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎮 DreamLeague S27 - Partidas de Hoje</h1>
                <p>{today} (Horário de Brasília)</p>
            </div>
        """
        
        for match in matches:
            html += f"""
            <div class="match">
                <div class="time">{match['countdown_color']} {match['time']} BRT - {match['countdown']}</div>
                <div class="teams">
                    <strong>{match['team_a']}</strong> vs <strong>{match['team_b']}</strong>
                </div>
                <div class="format">{match['format']}</div>
            </div>
            """
        
        html += """
            <p style="color: #888; font-size: 12px; margin-top: 30px;">
                🔥 Prometheus V7.3 - Sistema de Análise DreamLeague<br>
                Relatórios detalhados serão enviados 2 horas antes de cada série.
            </p>
        </body>
        </html>
        """
        
        return self.send_email(
            to_emails,
            f"🎮 DreamLeague S27 - Partidas {today}",
            html
        )
    
    def send_match_report(
        self, 
        match: Dict, 
        analysis: Dict,
        pdf_data: bytes = None,
        to_emails: List[str] = None
    ) -> bool:
        """Send detailed match report with PDF attachment."""
        if to_emails is None:
            to_emails = RECIPIENTS
        
        subject = f"📊 Relatório: {match['team_a']} vs {match['team_b']} - {match['countdown']}"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px; text-align: center; }}
                .section {{ background: #16213e; padding: 15px; margin: 15px 0; border-radius: 8px; }}
                .section h3 {{ color: #ffd700; margin-top: 0; }}
                .stat {{ display: inline-block; margin: 5px 10px; padding: 8px 15px; background: #0f3460; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Relatório Pré-Partida</h1>
                <h2>{match['team_a']} vs {match['team_b']}</h2>
                <p>{match['format']} - {match['time']} BRT</p>
            </div>
            
            <div class="section">
                <h3>🎯 Previsão</h3>
                <p>Favorito: <strong>{analysis.get('prediction', {}).get('winner', 'N/A')}</strong></p>
                <p>Confiança: <strong>{analysis.get('prediction', {}).get('confidence', 0):.0f}%</strong></p>
            </div>
            
            <div class="section">
                <h3>📈 Head-to-Head</h3>
                <p>Histórico: {analysis.get('h2h', {}).get('summary', 'N/A')}</p>
            </div>
            
            <div class="section">
                <h3>🔥 Form Recente</h3>
                <div class="stat">{match['team_a']}: {analysis.get('form_a', 'N/A')}</div>
                <div class="stat">{match['team_b']}: {analysis.get('form_b', 'N/A')}</div>
            </div>
            
            <p style="color: #888; font-size: 12px; margin-top: 30px;">
                🔥 Prometheus V7.3 - Análise gerada com IA Multi-Modelo<br>
                PDF com análise completa em anexo.
            </p>
        </body>
        </html>
        """
        
        attachments = []
        if pdf_data:
            filename = f"Relatorio_{match['team_a']}_vs_{match['team_b']}_{match['date']}.pdf"
            attachments.append({"filename": filename, "data": pdf_data})
        
        return self.send_email(to_emails, subject, html, attachments)


def calculate_match_countdown(match_datetime: datetime) -> Dict:
    """Calculate detailed countdown for a match."""
    hours = get_hours_until_match(match_datetime)
    
    return {
        "hours": hours,
        "formatted": format_countdown(hours),
        "color": get_countdown_color(hours),
        "is_live": hours < 0,
        "is_soon": 0 < hours < 2,
        "needs_report": 0 < hours <= 2
    }


# Scheduler functions (to be called by cron/scheduler)
def daily_morning_email():
    """Send daily morning email with today's matches."""
    notifier = EmailNotifier()
    return notifier.send_daily_schedule()


def check_and_send_reports():
    """Check for matches needing reports and send them."""
    matches = MatchSchedule.get_matches_needing_report()
    
    if not matches:
        return []
    
    notifier = EmailNotifier()
    sent = []
    
    for match in matches:
        # Generate analysis (placeholder - will integrate with AI)
        analysis = {
            "prediction": {"winner": match["team_a"], "confidence": 55},
            "h2h": {"summary": "3-2 nos últimos 5 confrontos"},
            "form_a": "W-W-L-W-W",
            "form_b": "L-W-W-L-W"
        }
        
        # TODO: Generate PDF with reportlab
        pdf_data = None
        
        if notifier.send_match_report(match, analysis, pdf_data):
            sent.append(match)
    
    return sent
