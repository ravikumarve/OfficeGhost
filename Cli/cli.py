"""
AI Office Pilot - Rich CLI Interface
Interactive command-line tool with rich formatting
"""

import sys
import time
import json
from typing import Optional

from core.pilot import AIOfficePilot
from core.config import Config


class CLI:
    """Rich CLI interface for AI Office Pilot"""

    def __init__(self, pilot: Optional[AIOfficePilot] = None) -> None:
        self.pilot = pilot
        self.rich_available = self._check_rich()

    def _check_rich(self) -> bool:
        """Check if rich is available"""
        try:
            from rich.console import Console
            from rich.table import Table
            from rich.progress import Progress

            return True
        except ImportError:
            return False

    def run(self) -> None:
        """Run the CLI"""
        if not self.pilot:
            print("Error: Not logged in. Please run main.py first.")
            return

        print("AI Office Pilot CLI v3.0")
        print("Type 'help' for available commands.\n")

        while True:
            try:
                cmd = input("pilot> ").strip()
                if not cmd:
                    continue

                self._handle_command(cmd)

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit.")
            except EOFError:
                break

    def _handle_command(self, cmd: str) -> None:
        """Handle a CLI command"""
        parts = cmd.split()
        action = parts[0].lower()

        if action == "help":
            self._cmd_help()
        elif action == "status":
            self._cmd_status()
        elif action == "cycle":
            self._cmd_cycle()
        elif action == "contacts":
            self._cmd_contacts(parts[1:] if len(parts) > 1 else [])
        elif action == "trust":
            self._cmd_trust(parts[1:] if len(parts) > 1 else [])
        elif action == "pending":
            self._cmd_pending()
        elif action == "send":
            self._cmd_send(parts[1:] if len(parts) > 1 else [])
        elif action == "drafts":
            self._cmd_drafts()
        elif action == "learning":
            self._cmd_learning()
        elif action == "dryrun":
            self._cmd_dryrun(parts[1:] if len(parts) > 1 else [])
        elif action == "exit":
            print("Goodbye!")
            sys.exit(0)
        else:
            print(f"Unknown command: {action}")
            print("Type 'help' for available commands.")

    def _cmd_help(self) -> None:
        """Show help message"""
        print("""
Available commands:
  status              - Show system status
  cycle               - Run one automation cycle
  contacts [list|add] - Manage contacts
  trust <email>       - Mark/unmark contact as trusted
  pending             - Show pending items (drafts, meetings)
  send <draft_id>     - Send a pending draft
  drafts              - List pending drafts
  learning            - Show learning report
  dryrun [on|off]     - Toggle dry-run mode
  help                - Show this help
  exit                - Exit CLI
""")

    def _cmd_status(self) -> None:
        """Show system status"""
        status = self.pilot.get_status()
        health = status["health"]

        print(f"""
System Status:
  Overall:  {health["overall"]}
  RAM:      {health["ram"]["used_gb"]}/{health["ram"]["total_gb"]}GB ({health["ram"]["percent"]}%)
  Disk:     {health["disk"]["free_gb"]}GB free
  Ollama:   {health["ollama"]["status"]}
  Cycles:   {status["cycles_completed"]}
  Queue:    {status["queue"]["pending"]} pending, {status["queue"]["completed"]} done
""")

    def _cmd_cycle(self) -> None:
        """Run automation cycle"""
        print("Running automation cycle...")
        result = self.pilot.run_cycle()

        print(f"""
Cycle #{result.get("cycle", "?")} complete:
  Emails processed: {result.get("emails_processed", 0)}
  Files organized:  {result.get("files_organized", 0)}
  Data entries:     {result.get("data_entries", 0)}
  Duration:         {result.get("duration_seconds", 0)}s
""")

        if result.get("errors"):
            print("Errors:")
            for e in result["errors"]:
                print(f"  - {e}")

    def _cmd_contacts(self, args: list) -> None:
        """Manage contacts"""
        if not args or args[0] == "list":
            contacts = self.pilot.memory.get_all_contacts()
            print(f"\nContacts ({len(contacts)}):")
            for c in contacts[:10]:
                trusted = "[TRUSTED]" if c.get("trusted") else ""
                print(f"  - {c.get('name', 'Unknown')} <{c['email']}> {trusted}")
            if len(contacts) > 10:
                print(f"  ... and {len(contacts) - 10} more")
        elif args[0] == "add":
            if len(args) < 2:
                print("Usage: contacts add <email>")
            else:
                email = args[1]
                self.pilot.memory.learn_contact(email)
                print(f"Added contact: {email}")

    def _cmd_trust(self, args: list) -> None:
        """Mark contact as trusted"""
        if len(args) < 1:
            print("Usage: trust <email> [on|off]")
            return

        email = args[0]
        trust = True
        if len(args) > 1 and args[1].lower() == "off":
            trust = False

        self.pilot.memory.set_trusted_contact(email, trust)
        action = "Trusted" if trust else "Untrusted"
        print(f"{action}: {email}")

    def _cmd_pending(self) -> None:
        """Show pending items"""
        from pathlib import Path

        drafts_dir = Config.PENDING_DIR / "drafts"
        meetings_dir = Config.CALENDAR_PENDING_DIR

        print("\nPending Items:")

        if drafts_dir.exists():
            drafts = list(drafts_dir.glob("*.json"))
            print(f"  Drafts: {len(drafts)}")
            for d in drafts[:5]:
                data = json.loads(d.read_text())
                email = data.get("original_email", {})
                print(f"    - {email.get('subject', 'Unknown')} -> {email.get('from', 'Unknown')}")
        else:
            print("  Drafts: 0")

        if meetings_dir.exists():
            meetings = list(meetings_dir.glob("*_meeting.json"))
            print(f"  Meetings: {len(meetings)}")
        else:
            print("  Meetings: 0")

    def _cmd_send(self, args: list) -> None:
        """Send a pending draft"""
        if len(args) < 1:
            print("Usage: send <draft_filename>")
            return

        draft_filename = args[0]
        if self.pilot.confirm_and_send(draft_filename):
            print(f"Sent: {draft_filename}")
        else:
            print(f"Failed to send: {draft_filename}")

    def _cmd_drafts(self) -> None:
        """List pending drafts"""
        from pathlib import Path

        drafts_dir = Config.PENDING_DIR / "drafts"
        if not drafts_dir.exists():
            print("No pending drafts.")
            return

        drafts = list(drafts_dir.glob("*.json"))
        print(f"\nPending Drafts ({len(drafts)}):")
        for d in drafts:
            data = json.loads(d.read_text())
            email = data.get("original_email", {})
            created = data.get("created_at", "Unknown")
            print(f"  {d.name}")
            print(f"    To: {email.get('from', 'Unknown')}")
            print(f"    Subject: {email.get('subject', 'Unknown')}")
            print(f"    Created: {created}")
            print()

    def _cmd_learning(self) -> None:
        """Show learning report"""
        report = self.pilot.memory.get_learning_report()

        print(f"""
Learning Report:
  Score:          {report.get("learning_score", 0)}/100
  Patterns:       {report.get("patterns_found", 0)} discovered
  Contacts:       {report.get("contacts_learned", 0)} learned
  Categories:     {report.get("categories_learned", 0)} mapped
  Total actions:  {report.get("total_actions", 0)}
""")

    def _cmd_dryrun(self, args: list) -> None:
        """Toggle dry-run mode"""
        if not args:
            status = "ON" if Config.DRY_RUN else "OFF"
            print(f"Dry-run mode: {status}")
        elif args[0].lower() == "on":
            Config.DRY_RUN = True
            print("Dry-run mode: ON")
        elif args[0].lower() == "off":
            Config.DRY_RUN = False
            print("Dry-run mode: OFF")


def run_cli() -> None:
    """Run the CLI tool"""
    try:
        from rich.console import Console
        from rich.table import Table

        cli = CLI()
        console = Console()

        console.print("[bold blue]AI Office Pilot CLI v3.0[/bold blue]")
        console.print("Type 'help' for available commands.\n")

        while True:
            cmd = console.input("\n[bold green]pilot>[/bold green] ")
            if not cmd.strip():
                continue

            parts = cmd.split()
            action = parts[0].lower()

            if action == "help":
                _show_help_table(console)
            elif action == "status":
                _show_status_table(console, cli)
            elif action == "exit":
                break

    except ImportError:
        print("Rich library not installed. Using basic CLI.")
        cli = CLI()
        cli.run()


def _show_help_table(console) -> None:
    """Show help with rich table"""
    from rich.table import Table

    table = Table(title="Available Commands")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="green")

    commands = [
        ("status", "Show system status"),
        ("cycle", "Run automation cycle"),
        ("contacts", "Manage contacts"),
        ("trust <email>", "Mark contact as trusted"),
        ("pending", "Show pending drafts/meetings"),
        ("drafts", "List pending drafts"),
        ("send <id>", "Send a draft"),
        ("learning", "Show learning report"),
        ("dryrun [on|off]", "Toggle dry-run mode"),
        ("help", "Show this help"),
        ("exit", "Exit CLI"),
    ]

    for cmd, desc in commands:
        table.add_row(cmd, desc)

    console.print(table)


def _show_status_table(console, cli) -> None:
    """Show status with rich table"""
    from rich.table import Table

    if not cli.pilot:
        console.print("[red]Not logged in.[/red]")
        return

    status = cli.pilot.get_status()
    health = status["health"]

    table = Table(title="System Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Overall", health["overall"])
    table.add_row("RAM", f"{health['ram']['percent']}%")
    table.add_row("Disk", f"{health['disk']['free_gb']}GB free")
    table.add_row("Ollama", health["ollama"]["status"])
    table.add_row("Cycles", str(status["cycles_completed"]))

    console.print(table)


if __name__ == "__main__":
    run_cli()
