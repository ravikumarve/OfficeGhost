#!/usr/bin/env python3
"""
AI Office Pilot - Entry Point
"""

import sys
import getpass
import argparse
from pathlib import Path

from core.pilot import AIOfficePilot
from core.config import Config
from security.auth import AccessControl


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="AI Office Pilot v3.0 - Your AI Office Assistant")
    parser.add_argument(
        "--dry-run", action="store_true", help="Run without sending emails or making changes"
    )
    parser.add_argument(
        "--test-email", action="store_true", help="Test email processing on unread emails"
    )
    parser.add_argument(
        "--test-files", action="store_true", help="Test file processing on watched folders"
    )
    parser.add_argument("--continuous", action="store_true", help="Run continuously")
    parser.add_argument("--status", action="store_true", help="Show status and exit")
    return parser.parse_args()


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║              🤖 AI OFFICE PILOT v3.0                        ║
║     Email + Files + Data • Self-Learning • Encrypted       ║
╚══════════════════════════════════════════════════════════════╝
    """)


def first_time_setup(pilot):
    """Interactive first-time setup"""
    print("\n🔧 FIRST TIME SETUP")
    print("=" * 50)
    print("\nYour data will be encrypted with a master password.")
    print("This password is NEVER stored. If you forget it,")
    print("your data CANNOT be recovered (this is a feature).\n")

    while True:
        password = getpass.getpass("Create master password (min 12 chars): ")

        if len(password) < 12:
            print("❌ Password must be at least 12 characters\n")
            continue

        strength = AccessControl.check_password_strength(password)
        print(f"   Strength: [{strength['bar']}] {strength['label']}")

        if strength["feedback"]:
            for tip in strength["feedback"]:
                print(f"   💡 {tip}")

        confirm = getpass.getpass("Confirm password: ")

        if password != confirm:
            print("❌ Passwords don't match\n")
            continue

        break

    pilot.first_time_setup(password)
    print("\n✅ Setup complete! Your AI Office Pilot is ready.\n")

    return password


def main():
    args = parse_args()

    # Handle dry-run mode
    if args.dry_run:
        Config.DRY_RUN = True
        print("\n🔍 DRY RUN MODE - No emails will be sent or changes made\n")

    print_banner()

    # Validate configuration
    errors = Config.validate()
    if errors:
        print("⚠️ Configuration warnings:")
        for error in errors:
            print(f"   • {error}")
        print()

    # Handle --status flag
    if args.status:
        pilot = AIOfficePilot()
        if pilot.crypto.is_setup:
            password = getpass.getpass("Master password: ")
            try:
                pilot.login(password)
                status = pilot.get_status()
                print_status(status)
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
        else:
            print("System not initialized. Run without --status to set up.")
        sys.exit(0)

    # Handle test modes
    if args.test_email or args.test_files:
        pilot = AIOfficePilot()
        if pilot.crypto.is_setup:
            password = getpass.getpass("Master password: ")
            pilot.login(password)
        else:
            print("System not initialized.")
            sys.exit(1)

        if args.test_email:
            print("\n📧 Testing email processing...")
            result = pilot.run_cycle()
            print(f"\n   Processed: {result.get('emails_processed', 0)} emails")

        if args.test_files:
            print("\n📁 Testing file processing...")
            new_files = pilot.file_watcher.scan_new()
            print(f"\n   Found: {len(new_files)} new files")

        pilot.shutdown()
        sys.exit(0)

    # Create pilot
    pilot = AIOfficePilot()

    # Check if first time
    if not pilot.crypto.is_setup:
        password = first_time_setup(pilot)
    else:
        password = getpass.getpass("🔒 Master password: ")

    # Login
    try:
        pilot.login(password)
    except Exception as e:
        print(f"\n❌ {e}")
        sys.exit(1)

    print("🔓 Authenticated successfully!\n")

    # Show status
    status = pilot.get_status()
    health = status["health"]
    security = status["security"]

    print(f"   System:     {health['overall']}")
    print(f"   RAM:        {health['ram']['status']} {health['ram']['percent']}%")
    print(f"   Disk:       {health['disk']['status']} {health['disk']['free_gb']}GB free")
    print(f"   Ollama:     {health['ollama']['status']}")
    print(f"   Security:   {security['overall']}")
    print(f"   Encryption: 🟢 AES-256 Active")

    if pilot.memory:
        learning = status["learning"]
        print(f"   Learning:   Score {learning['learning_score']}/100")

    print()

    # Menu
    while True:
        dry_run_note = " [DRY RUN]" if Config.DRY_RUN else ""
        print(f"\n📋 MENU{dry_run_note}:")
        print("   [1] Run single cycle")
        print("   [2] Run continuously")
        print("   [3] View status dashboard")
        print("   [4] View learning report")
        print("   [5] View security status")
        print("   [6] Create backup")
        print("   [7] Compliance report")
        print("   [8] Export my data")
        print("   [9] Settings")
        print("   [a] Manage trusted contacts")
        print("   [d] Toggle dry-run mode")
        print("   [0] Shutdown & exit")

        choice = input("\n   Choice: ").strip()

        if choice == "1":
            result = pilot.run_cycle()
            print(f"\n   Cycle complete:")
            print(f"      Emails: {result.get('emails_processed', 0)}")
            print(f"      Files: {result.get('files_organized', 0)}")
            print(f"      Data: {result.get('data_entries', 0)}")
            if result.get("errors"):
                for e in result["errors"]:
                    print(f"      Warning: {e}")

        elif choice == "2":
            pilot.run_continuous()

        elif choice == "3":
            status = pilot.get_status()
            _print_status(status)

        elif choice == "4":
            if pilot.memory:
                report = pilot.memory.get_learning_report()
                _print_learning(report)

        elif choice == "5":
            sec = pilot.threats.get_status()
            _print_security(sec)

        elif choice == "6":
            path = pilot.backup.create_backup()
            print(f"\n   Backup created: {path}")

        elif choice == "7":
            result = pilot.compliance.generate_report()
            print(f"\n   Report saved: {result['audit_report']}")

        elif choice == "8":
            path = Config.REPORT_DIR / "my_data_export.json"
            pilot.lifecycle.export_all_data(path)
            print(f"\n   Data exported: {path}")

        elif choice == "9":
            print("\n   Settings configured via .env file")
            print(f"   Location: {Config.BASE_DIR / '.env'}")

        elif choice == "a":
            _manage_trusted_contacts(pilot)

        elif choice == "d":
            Config.DRY_RUN = not Config.DRY_RUN
            mode = "ENABLED" if Config.DRY_RUN else "DISABLED"
            print(f"\n   Dry-run mode {mode}")
            if Config.DRY_RUN:
                print("   No emails will be sent or changes made")

        elif choice == "0":
            pilot.shutdown()
            print("\n   Goodbye!\n")
            break

        else:
            print("   Invalid choice")


def _print_status(status):
    """Print formatted status"""
    h = status["health"]
    print(f"\n   ═══ SYSTEM STATUS ═══")
    print(f"   Overall:    {h['overall']}")
    print(f"   RAM:        {h['ram']['used_gb']}/{h['ram']['total_gb']}GB ({h['ram']['percent']}%)")
    print(f"   Disk:       {h['disk']['free_gb']}GB free ({h['disk']['percent_used']}% used)")
    print(
        f"   Queue:      {status['queue']['pending']} pending, {status['queue']['completed']} done"
    )
    print(f"   Cycles:     {status['cycles_completed']}")


def _print_learning(report):
    """Print learning report"""
    score = report["learning_score"]
    bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
    print(f"\n   ═══ LEARNING REPORT ═══")
    print(f"   Score:      [{bar}] {score}/100")
    print(f"   Accuracy:   {report['accuracy']}")
    print(f"   Patterns:   {report['patterns_found']} discovered")
    print(f"   Contacts:   {report['contacts_learned']} learned")
    print(f"   Categories: {report['categories_learned']} mapped")
    print(f"   Actions:    {report['total_actions']} logged")

    if report["patterns"]:
        print(f"\n   Top Patterns:")
        for p in report["patterns"][:5]:
            print(f"      • {p['description']} ({p['confidence'] * 100:.0f}%)")


def _print_security(sec):
    """Print security status"""
    print(f"\n   ═══ SECURITY STATUS ═══")
    print(f"   Overall:    {sec['overall']}")
    print(f"   Network:    {'Isolated' if sec['network_isolated'] else 'Not isolated'}")
    print(f"   Alerts:     {sec['recent_alerts']} in last 24h")

    if sec.get("alerts"):
        for a in sec["alerts"][-5:]:
            print(f"      [{a['severity']}] {a['type']}: {a['detail']}")


def print_status(status):
    """Print formatted status (for --status flag)"""
    h = status["health"]
    print(f"\n   ═══ SYSTEM STATUS ═══")
    print(f"   Overall:    {h['overall']}")
    print(f"   RAM:        {h['ram']['used_gb']}/{h['ram']['total_gb']}GB ({h['ram']['percent']}%)")
    print(f"   Disk:       {h['disk']['free_gb']}GB free")
    print(f"   Ollama:     {h['ollama']['status']}")
    print(f"   Encryption: Active")


def _manage_trusted_contacts(pilot):
    """Manage trusted contacts for auto-send"""
    print("\n   ═══ TRUSTED CONTACTS ═══")

    contacts = pilot.memory.get_all_contacts()
    trusted = pilot.memory.get_trusted_contacts()

    print(f"   Total contacts: {len(contacts)}")
    print(f"   Trusted: {len(trusted)}\n")

    if trusted:
        print("   Trusted contacts:")
        for c in trusted:
            print(f"      • {c.get('name', 'Unknown')} ({c['email']})")
    else:
        print("   No trusted contacts yet.")
        print("   Mark contacts as trusted to enable auto-send.")

    print("\n   Options:")
    print("   [a] Add trusted contact")
    print("   [r] Remove trusted contact")
    print("   [b] Back")

    choice = input("\n   Choice: ").strip()

    if choice == "a":
        email = input("   Enter email address: ").strip()
        if email:
            pilot.memory.set_trusted_contact(email, True)
            print(f"   ✓ {email} marked as trusted")
    elif choice == "r":
        email = input("   Enter email address: ").strip()
        if email:
            pilot.memory.set_trusted_contact(email, False)
            print(f"   ✓ {email} removed from trusted")


if __name__ == "__main__":
    main()
