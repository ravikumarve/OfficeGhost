"""
AI Office Pilot - Security Configuration
IP allowlisting, network isolation, and VPN settings
"""

import os
import socket
import subprocess
import logging
import ipaddress
from typing import Optional, Callable, List
from functools import wraps
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

from core.config import Config

logger = logging.getLogger(__name__)


class NetworkMode(Enum):
    """Network connectivity modes"""
    NORMAL = "normal"  # Full network access
    ISOLATED = "isolated"  # Local network only
    AIR_GAPPED = "air_gapped"  # No network access


@dataclass
class VPNConfig:
    """VPN configuration"""
    enabled: bool = False
    vpn_name: str = ""
    auto_connect: bool = False
    check_on_startup: bool = True


class NetworkIsolation:
    """Network isolation mode - for secure air-gapped operation"""

    def __init__(self) -> None:
        self._mode = self._get_configured_mode()
        self._vpn_config = self._load_vpn_config()
        self._allowed_services = self._load_allowed_services()

    def _get_configured_mode(self) -> NetworkMode:
        """Get configured network mode"""
        mode_str = os.getenv("NETWORK_MODE", "normal").lower()
        try:
            return NetworkMode(mode_str)
        except ValueError:
            logger.warning(f"Invalid NETWORK_MODE: {mode_str}, using NORMAL")
            return NetworkMode.NORMAL

    def _load_vpn_config(self) -> VPNConfig:
        """Load VPN configuration from environment"""
        return VPNConfig(
            enabled=os.getenv("VPN_ENABLED", "false").lower() == "true",
            vpn_name=os.getenv("VPN_NAME", ""),
            auto_connect=os.getenv("VPN_AUTO_CONNECT", "false").lower() == "true",
            check_on_startup=os.getenv("VPN_CHECK_ON_STARTUP", "true").lower() == "true"
        )

    def _load_allowed_services(self) -> List[str]:
        """Load allowed external services for isolated mode"""
        services_str = os.getenv("ALLOWED_SERVICES", "ollama.local")
        return [s.strip() for s in services_str.split(",") if s.strip()]

    def get_mode(self) -> NetworkMode:
        """Get current network mode"""
        return self._mode

    def set_mode(self, mode: NetworkMode) -> None:
        """Set network mode"""
        self._mode = mode
        logger.info(f"Network mode set to: {mode.value}")

    def is_isolated(self) -> bool:
        """Check if running in isolated mode"""
        return self._mode in (NetworkMode.ISOLATED, NetworkMode.AIR_GAPPED)

    def can_connect(self, host: str) -> bool:
        """Check if connection to host is allowed"""
        if self._mode == NetworkMode.NORMAL:
            return True

        if self._mode == NetworkMode.AIR_GAPPED:
            return False

        # Isolated mode: allow local and configured services
        # Check if it's a local IP
        try:
            ip = socket.gethostbyname(host)
            if ipaddress.ip_address(ip).is_private:
                return True
        except socket.gaierror:
            pass

        # Check allowed services
        return host in self._allowed_services or host == "localhost"

    def get_vpn_status(self) -> dict:
        """Get VPN connection status"""
        if not self._vpn_config.enabled:
            return {"enabled": False, "connected": False}

        connected = self._check_vpn_connection()
        return {
            "enabled": True,
            "vpn_name": self._vpn_config.vpn_name,
            "connected": connected,
            "auto_connect": self._vpn_config.auto_connect
        }

    def _check_vpn_connection(self) -> bool:
        """Check if VPN is connected"""
        if not self._vpn_config.enabled:
            return False

        try:
            # Check common VPN interface names
            result = subprocess.run(
                ["ip", "addr", "show"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Look for common VPN interface patterns
            vpn_patterns = ["tun", "tap", "wg", "vpn"]
            for line in result.stdout.split("\n"):
                for pattern in vpn_patterns:
                    if pattern in line.lower() and "inet" in line:
                        return True
        except Exception as e:
            logger.debug(f"VPN check failed: {e}")

        return False

    def connect_vpn(self) -> bool:
        """Connect to configured VPN"""
        if not self._vpn_config.enabled or not self._vpn_config.vpn_name:
            return False

        logger.info(f"Connecting to VPN: {self._vpn_config.vpn_name}")
        # Implementation would use NetworkManager API or similar
        return True

    def disconnect_vpn(self) -> bool:
        """Disconnect from VPN"""
        logger.info("Disconnecting VPN")
        return True

    def get_status(self) -> dict:
        """Get network security status"""
        return {
            "mode": self._mode.value,
            "isolated": self.is_isolated(),
            "vpn": self.get_vpn_status(),
            "allowed_services": self._allowed_services
        }


class IPAllowlist:

    def _load_config(self) -> None:
        """Load allowlist from config"""
        # Get allowed IPs from config
        allowed_str = os.getenv("ALLOWED_IPS", "")
        if allowed_str:
            for ip in allowed_str.split(","):
                ip = ip.strip()
                if "/" in ip:
                    # CIDR notation
                    try:
                        self._allowed_networks.append(ipaddress.IPv4Network(ip, strict=False))
                    except ValueError:
                        pass
                else:
                    self._allowed_ips.add(ip)

        # Add localhost by default
        self._allowed_ips.add("127.0.0.1")
        self._allowed_ips.add("::1")

    def is_enabled(self) -> bool:
        """Check if IP allowlisting is enabled"""
        return os.getenv("ENABLE_IP_ALLOWLIST", "false").lower() == "true"

    def is_allowed(self, ip: str) -> bool:
        """Check if IP is allowed"""
        # If not enabled, allow all
        if not self.is_enabled():
            return True

        # Check blocked
        if ip in self._blocked_ips:
            blocked_until = self._blocked_ips[ip]
            if datetime.now() < blocked_until:
                return False
            else:
                del self._blocked_ips[ip]

        # Check direct IP match
        if ip in self._allowed_ips:
            return True

        # Check network matches
        try:
            ip_obj = ipaddress.ip_address(ip)
            for network in self._allowed_networks:
                if ip_obj in network:
                    return True
        except ValueError:
            pass

        return False

    def block_ip(self, ip: str, duration_minutes: int = 60) -> None:
        """Block an IP address temporarily"""
        self._blocked_ips[ip] = datetime.now() + timedelta(minutes=duration_minutes)

    def get_client_ip(self, request) -> str:
        """Extract client IP from request (handles proxies)"""
        # Check X-Forwarded-For header first (for proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to remote_addr
        return request.remote_addr or "0.0.0.0"


# Global allowlist instance
_ip_allowlist: Optional[IPAllowlist] = None


def get_allowlist() -> IPAllowlist:
    """Get the global IP allowlist instance"""
    global _ip_allowlist
    if _ip_allowlist is None:
        _ip_allowlist = IPAllowlist()
    return _ip_allowlist


def check_ip_allowlist(request) -> bool:
    """Check if request IP is allowed"""
    allowlist = get_allowlist()
    if not allowlist.is_enabled():
        return True

    client_ip = allowlist.get_client_ip(request)
    return allowlist.is_allowed(client_ip)
