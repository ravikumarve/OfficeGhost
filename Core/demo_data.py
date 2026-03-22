"""
GhostOffice - Demo Data
Sample data for dashboard evaluation and screenshots
"""

from datetime import datetime, timedelta
import random


DEMO_MODE = True


def get_demo_emails():
    """15 sample processed emails with varied classifications"""
    
    base_time = datetime.now()
    
    return [
        # URGENT - 5 emails
        {
            "id": 1,
            "classification": "URGENT",
            "sender": "billing@acmecorp.com",
            "sender_name": "Acme Corp Billing",
            "subject": "Invoice #4521 Past Due - Payment Required Within 48 Hours",
            "preview": "Your invoice for $2,847.50 is now 15 days overdue. Please process payment immediately to avoid service interruption.",
            "confidence": 97,
            "timestamp": (base_time - timedelta(hours=2)).isoformat(),
            "action_taken": "Flagged for immediate attention",
        },
        {
            "id": 2,
            "classification": "URGENT",
            "sender": "alerts@aws.amazon.com",
            "sender_name": "AWS System Alerts",
            "subject": "CRITICAL: Production Server CPU at 98% - Immediate Action Required",
            "preview": "Your EC2 instance i-0abc123def456 is experiencing sustained high CPU utilization. Auto-scaling has been triggered.",
            "confidence": 99,
            "timestamp": (base_time - timedelta(hours=4)).isoformat(),
            "action_taken": "Alert sent to admin",
        },
        {
            "id": 3,
            "classification": "URGENT",
            "sender": "hr@company.com",
            "sender_name": "HR Department",
            "subject": "URGENT: Benefits Enrollment Deadline - Today at 5PM",
            "preview": "This is a final reminder that open enrollment closes today. Missing this deadline means no coverage until January.",
            "confidence": 94,
            "timestamp": (base_time - timedelta(hours=1)).isoformat(),
            "action_taken": "Notification sent",
        },
        {
            "id": 4,
            "classification": "URGENT",
            "sender": "security@bank.com",
            "sender_name": "Bank Security Team",
            "subject": "Suspicious Activity Detected on Your Account - Verify Now",
            "preview": "We detected a login attempt from an unrecognized device in Russia. If this wasn't you, please secure your account immediately.",
            "confidence": 96,
            "timestamp": (base_time - timedelta(hours=6)).isoformat(),
            "action_taken": "Flagged for review",
        },
        {
            "id": 5,
            "classification": "URGENT",
            "sender": "support@ticketsystem.com",
            "sender_name": "Ticket System",
            "subject": "Ticket #8921: Production Database Connection Timeout",
            "preview": "Multiple customers reporting connection timeouts. Engineering team needs immediate escalation. Current impact: 200+ affected users.",
            "confidence": 98,
            "timestamp": (base_time - timedelta(minutes=30)).isoformat(),
            "action_taken": "Escalated to on-call team",
        },
        
        # ROUTINE - 5 emails
        {
            "id": 6,
            "classification": "ROUTINE",
            "sender": "newsletter@techweekly.com",
            "sender_name": "Tech Weekly Newsletter",
            "subject": "This Week in Tech: AI Advances, New Frameworks, and Developer Tips",
            "preview": "Top stories: GPT-5 released, React 20 introduces new hooks, VS Code gets AI pair programmer...",
            "confidence": 92,
            "timestamp": (base_time - timedelta(days=1)).isoformat(),
            "action_taken": "Archived",
        },
        {
            "id": 7,
            "classification": "ROUTINE",
            "sender": "notes@company.com",
            "sender_name": "Team Notes Bot",
            "subject": "Meeting Notes: Sprint Planning - March 15, 2026",
            "preview": "Attendees: Sarah, Mike, Lisa, Tom. Key decisions: Ship v2.3 by April 1, prioritize mobile app...",
            "confidence": 89,
            "timestamp": (base_time - timedelta(days=1, hours=3)).isoformat(),
            "action_taken": "Summary saved",
        },
        {
            "id": 8,
            "classification": "ROUTINE",
            "sender": "receipts@amazon.com",
            "sender_name": "Amazon",
            "subject": "Your Amazon.com order has shipped - Track Package",
            "preview": "Your package is on its way! Arriving: March 24. Items: USB-C Hub, Desk Organizer, Coffee Beans...",
            "confidence": 95,
            "timestamp": (base_time - timedelta(days=2)).isoformat(),
            "action_taken": "Receipt filed",
        },
        {
            "id": 9,
            "classification": "ROUTINE",
            "sender": "github@noreply.github.com",
            "sender_name": "GitHub",
            "subject": "[ghostoffice/officeghost] PR #45: Add notification bell feature",
            "preview": "@developer merged 3 hours ago - Added notification bell icon to dashboard header...",
            "confidence": 91,
            "timestamp": (base_time - timedelta(days=3)).isoformat(),
            "action_taken": "Reviewed",
        },
        {
            "id": 10,
            "classification": "ROUTINE",
            "sender": "updates@linkedin.com",
            "sender_name": "LinkedIn",
            "subject": "You have 3 new connections and 12 profile views this week",
            "preview": "John Smith, Emily Chen, and Robert Kim want to connect. Your profile got 12 views from recruiters at Google, Meta, and Amazon.",
            "confidence": 88,
            "timestamp": (base_time - timedelta(days=4)).isoformat(),
            "action_taken": "Dismissed",
        },
        
        # SPAM - 3 emails
        {
            "id": 11,
            "classification": "SPAM",
            "sender": "winner@lottery-intl.com",
            "sender_name": "International Lottery",
            "subject": "CONGRATULATIONS! You've Won $5,000,000 in Our Mega Draw!",
            "preview": "Your email address was randomly selected as the winner of our international lottery. Claim your prize now!",
            "confidence": 99,
            "timestamp": (base_time - timedelta(days=2)).isoformat(),
            "action_taken": "Marked as spam",
        },
        {
            "id": 12,
            "classification": "SPAM",
            "sender": "deals@bestbuy-promo.com",
            "sender_name": "Best Buy Deals",
            "subject": "🔥 LIMITED TIME: 90% OFF All Electronics - While Supplies Last!",
            "preview": "Massive clearance sale! MacBook Pro $199, iPhone 16 $49, 80\" TV $299. Click now before it's gone!",
            "confidence": 97,
            "timestamp": (base_time - timedelta(days=5)).isoformat(),
            "action_taken": "Marked as spam",
        },
        {
            "id": 13,
            "classification": "SPAM",
            "sender": "ceo@urgent-business.com",
            "sender_name": "Dr. James Wilson",
            "subject": "URGENT: Confidential Business Proposal - Reply Immediately",
            "preview": "I represent a deceased client who left $45.5 million unclaimed. Help me transfer this funds...",
            "confidence": 99,
            "timestamp": (base_time - timedelta(days=1)).isoformat(),
            "action_taken": "Marked as spam",
        },
        
        # MEETING - 2 emails
        {
            "id": 14,
            "classification": "MEETING",
            "sender": "calendar@company.com",
            "sender_name": "Google Calendar",
            "subject": "Invitation: Q1 Review Meeting on Mar 25, 2026 at 2:00 PM",
            "preview": "You're invited to Q1 Review Meeting. When: Tuesday, March 25, 2026, 2:00 PM - 3:30 PM (PST). Where: Conference Room A / Zoom",
            "confidence": 93,
            "timestamp": (base_time - timedelta(hours=8)).isoformat(),
            "action_taken": "Added to calendar",
        },
        {
            "id": 15,
            "classification": "MEETING",
            "sender": "alex@startup.io",
            "sender_name": "Alex Chen",
            "subject": "Re: Quick sync tomorrow? - 30 min",
            "preview": "Hey! Want to hop on a quick call tomorrow to discuss the new feature? I have some ideas I'd love to get your input on.",
            "confidence": 87,
            "timestamp": (base_time - timedelta(hours=12)).isoformat(),
            "action_taken": "Calendar invite sent",
        },
    ]


def get_demo_files():
    """20 sample file operations"""
    
    base_time = datetime.now()
    
    return [
        {"operation": "sorted", "filename": "Q1_Report_2026.pdf", "category": "Reports", "size_mb": 2.4, "timestamp": (base_time - timedelta(hours=1)).isoformat()},
        {"operation": "sorted", "filename": "Invoice_March_2026.xlsx", "category": "Finance/Invoices", "size_mb": 0.3, "timestamp": (base_time - timedelta(hours=2)).isoformat()},
        {"operation": "sorted", "filename": "Employment_Contract_Smith.pdf", "category": "Legal/Contracts", "size_mb": 1.1, "timestamp": (base_time - timedelta(hours=3)).isoformat()},
        {"operation": "sorted", "filename": "Presentation_Deck_v2.pptx", "category": "Presentations", "size_mb": 15.7, "timestamp": (base_time - timedelta(hours=4)).isoformat()},
        {"operation": "sorted", "filename": "receipt_amazon_0320.pdf", "category": "Finance/Receipts", "size_mb": 0.1, "timestamp": (base_time - timedelta(hours=5)).isoformat()},
        {"operation": "sorted", "filename": "team_photo.jpg", "category": "Images", "size_mb": 4.2, "timestamp": (base_time - timedelta(hours=6)).isoformat()},
        {"operation": "sorted", "filename": "Budget_Tracker_2026.xlsx", "category": "Spreadsheets", "size_mb": 0.8, "timestamp": (base_time - timedelta(hours=8)).isoformat()},
        {"operation": "sorted", "filename": "Meeting_Notes_0315.txt", "category": "Correspondence", "size_mb": 0.02, "timestamp": (base_time - timedelta(hours=10)).isoformat()},
        {"operation": "sorted", "filename": "Tax_Form_W9_2026.pdf", "category": "Finance/Tax", "size_mb": 0.5, "timestamp": (base_time - timedelta(days=1)).isoformat()},
        {"operation": "sorted", "filename": "Insurance_Policy_2026.pdf", "category": "Insurance", "size_mb": 1.8, "timestamp": (base_time - timedelta(days=1, hours=2)).isoformat()},
        {"operation": "duplicate", "filename": "Report_Final_v2.pdf", "category": "Reports", "size_mb": 2.4, "original": "Report_Final_v1.pdf", "timestamp": (base_time - timedelta(days=1, hours=4)).isoformat()},
        {"operation": "duplicate", "filename": "Presentation_backup.pptx", "category": "Presentations", "size_mb": 15.7, "original": "Presentation_Deck.pptx", "timestamp": (base_time - timedelta(days=2)).isoformat()},
        {"operation": "duplicate", "filename": "invoice_march_copy.xlsx", "category": "Finance/Invoices", "size_mb": 0.3, "original": "Invoice_March_2026.xlsx", "timestamp": (base_time - timedelta(days=2, hours=3)).isoformat()},
        {"operation": "analyzed", "filename": "Contract_Draft_2026.pdf", "category": "Legal/Contracts", "size_mb": 2.1, "entities": "14 signers, 3 dates, $45000 amount", "timestamp": (base_time - timedelta(days=3)).isoformat()},
        {"operation": "analyzed", "filename": "Invoice_Bulk_March.pdf", "category": "Finance/Invoices", "size_mb": 0.9, "entities": "12 line items, $12450 total", "timestamp": (base_time - timedelta(days=3, hours=2)).isoformat()},
        {"operation": "analyzed", "filename": "Resume_Johnson.pdf", "category": "HR/Resumes", "size_mb": 0.6, "entities": "5 skills extracted, 2 prior employers", "timestamp": (base_time - timedelta(days=4)).isoformat()},
        {"operation": "analyzed", "filename": "Medical_Statement_0226.pdf", "category": "Medical", "size_mb": 0.4, "entities": "3 providers, $850 patient responsibility", "timestamp": (base_time - timedelta(days=5)).isoformat()},
        {"operation": "sorted", "filename": "Quarterly_Results.xlsx", "category": "Reports", "size_mb": 3.2, "timestamp": (base_time - timedelta(days=6)).isoformat()},
        {"operation": "sorted", "filename": "Client_Proposal_v3.pdf", "category": "Correspondence", "size_mb": 4.5, "timestamp": (base_time - timedelta(days=7)).isoformat()},
    ]


def get_demo_learning():
    """Sample learning data"""
    
    return {
        "learning_score": 67.5,
        "feedback_count": 23,
        "style_traits": 8,
        "patterns_found": 12,
        "contacts_learned": 31,
        "accuracy": {
            "email_reply": {"accuracy": 94, "samples": 47},
            "file_categorize": {"accuracy": 87, "samples": 156},
            "data_extract": {"accuracy": 91, "samples": 28},
        },
        "patterns": [
            {"type": "time_based", "description": "Check emails at 9AM and 3PM", "confidence": 0.92},
            {"type": "chain", "description": "Invoice emails → Finance folder", "confidence": 0.88},
            {"type": "time_based", "description": "Review reports on Mondays", "confidence": 0.85},
        ],
        "recent_history": [
            {"date": "2026-03-20", "score": 62},
            {"date": "2026-03-19", "score": 60},
            {"date": "2026-03-18", "score": 58},
            {"date": "2026-03-17", "score": 55},
            {"date": "2026-03-16", "score": 52},
            {"date": "2026-03-15", "score": 48},
            {"date": "2026-03-14", "score": 45},
        ],
    }


def get_demo_notifications():
    """Sample notification events"""
    
    base_time = datetime.now()
    
    return [
        {"category": "success", "title": "Files Organized", "message": "18 files sorted into categories", "created_at": (base_time - timedelta(minutes=15)).isoformat()},
        {"category": "success", "title": "Duplicates Detected", "message": "3 duplicate files found and reported", "created_at": (base_time - timedelta(minutes=45)).isoformat()},
        {"category": "task", "title": "Email Scan Complete", "message": "Processed 15 emails in 2.3 seconds", "created_at": (base_time - timedelta(hours=1)).isoformat()},
        {"category": "security", "title": "Session Started", "message": "New secure session from Chrome on Linux", "created_at": (base_time - timedelta(hours=2)).isoformat()},
        {"category": "success", "title": "Data Extracted", "message": "Invoice data saved to expenses.xlsx", "created_at": (base_time - timedelta(hours=3)).isoformat()},
    ]


def get_demo_stats():
    """Dashboard statistics"""
    
    return {
        "total_emails": 47,
        "urgent_count": 8,
        "routine_count": 31,
        "spam_count": 6,
        "meeting_count": 2,
        "files_processed": 156,
        "duplicates_found": 12,
        "data_entries": 89,
        "cycles_completed": 23,
    }


def get_demo_status():
    """Full system status for dashboard"""
    
    return {
        "health": {
            "overall": "Healthy",
            "ram": {"percent": 42, "used_gb": 6.8, "total_gb": 16},
            "disk": {"percent": 58, "free_gb": 420, "total_gb": 1000},
            "cpu": {"percent": 15},
        },
        "security": {
            "overall": "Fully Secure",
        },
        "encryption": {
            "setup": True,
            "unlocked": True,
        },
        "learning": get_demo_learning(),
        "queue": {
            "pending": 0,
            "completed": 156,
            "failed": 2,
        },
        "cycles_completed": 23,
    }
