"""Tests for HealthMonitor class"""

import pytest
from unittest.mock import MagicMock, patch


class TestHealthMonitor:
    """Test cases for HealthMonitor"""

    def test_init(self, mock_config):
        """Test HealthMonitor initialization"""
        from core.health_monitor import HealthMonitor

        monitor = HealthMonitor()

        assert monitor.RAM_WARNING_THRESHOLD == 85
        assert monitor.RAM_GREEN_THRESHOLD == 80
        assert monitor.DISK_WARNING_GB == 5

    def test_check_ram_green(self, mock_config):
        """Test RAM check when healthy"""
        from core.health_monitor import HealthMonitor

        monitor = HealthMonitor()

        with patch("core.health_monitor.psutil") as mock_psutil:
            mock_mem = MagicMock()
            mock_mem.percent = 50
            mock_mem.total = 16 * 1024**3
            mock_mem.used = 8 * 1024**3
            mock_mem.available = 8 * 1024**3
            mock_psutil.virtual_memory.return_value = mock_mem

            result = monitor.check_ram()

            assert result["percent"] == 50
            assert result["status"] == "🟢"
            assert result["warning"] is False

    def test_check_ram_yellow(self, mock_config):
        """Test RAM check when warning"""
        from core.health_monitor import HealthMonitor

        monitor = HealthMonitor()

        with patch("core.health_monitor.psutil") as mock_psutil:
            mock_mem = MagicMock()
            mock_mem.percent = 85
            mock_mem.total = 16 * 1024**3
            mock_mem.used = 14 * 1024**3
            mock_mem.available = 2 * 1024**3
            mock_psutil.virtual_memory.return_value = mock_mem

            result = monitor.check_ram()

            assert result["percent"] == 85
            assert result["status"] == "🟡"
            assert result["warning"] is True

    def test_check_ram_red(self, mock_config):
        """Test RAM check when critical"""
        from core.health_monitor import HealthMonitor

        monitor = HealthMonitor()

        with patch("core.health_monitor.psutil") as mock_psutil:
            mock_mem = MagicMock()
            mock_mem.percent = 95
            mock_mem.total = 16 * 1024**3
            mock_mem.used = 15 * 1024**3
            mock_mem.available = 1 * 1024**3
            mock_psutil.virtual_memory.return_value = mock_mem

            result = monitor.check_ram()

            assert result["percent"] == 95
            assert result["status"] == "🔴"
            assert result["warning"] is True

    def test_check_disk_green(self, mock_config, temp_dir):
        """Test disk check when healthy"""
        from core.health_monitor import HealthMonitor

        monitor = HealthMonitor()

        with patch.object(mock_config, "DATA_DIR", temp_dir):
            with patch("core.health_monitor.shutil") as mock_shutil:
                mock_usage = MagicMock()
                mock_usage.free = 100 * 1024**3  # 100GB
                mock_usage.total = 500 * 1024**3  # 500GB
                mock_usage.used = 400 * 1024**3
                mock_shutil.disk_usage.return_value = mock_usage

                result = monitor.check_disk()

                assert result["free_gb"] > 10
                assert result["status"] == "🟢"

    def test_check_disk_warning(self, mock_config, temp_dir):
        """Test disk check when warning"""
        from core.health_monitor import HealthMonitor

        monitor = HealthMonitor()

        with patch.object(mock_config, "DATA_DIR", temp_dir):
            with patch("core.health_monitor.shutil") as mock_shutil:
                mock_usage = MagicMock()
                mock_usage.free = 6 * 1024**3  # 6GB
                mock_usage.total = 500 * 1024**3
                mock_usage.used = 494 * 1024**3
                mock_shutil.disk_usage.return_value = mock_usage

                result = monitor.check_disk()

                assert result["status"] == "🟡"
                assert result["warning"] is True

    def test_check_disk_critical(self, mock_config, temp_dir):
        """Test disk check when critical"""
        from core.health_monitor import HealthMonitor

        monitor = HealthMonitor()

        with patch.object(mock_config, "DATA_DIR", temp_dir):
            with patch("core.health_monitor.shutil") as mock_shutil:
                mock_usage = MagicMock()
                mock_usage.free = 3 * 1024**3  # 3GB
                mock_usage.total = 500 * 1024**3
                mock_usage.used = 497 * 1024**3
                mock_shutil.disk_usage.return_value = mock_usage

                result = monitor.check_disk()

                assert result["status"] == "🔴"
                assert result["warning"] is True

    @patch("core.retry.requests.get")
    def test_check_ollama_running(self, mock_get, mock_config):
        """Test Ollama check when running"""
        from core.health_monitor import HealthMonitor

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "phi3:mini"}]}
        mock_get.return_value = mock_response

        monitor = HealthMonitor()
        result = monitor.check_ollama()

        assert result["running"] is True
        assert result["status"] == "🟢"
        assert result["models_loaded"] == 1

    @patch("core.retry.requests.get")
    def test_check_ollama_not_running(self, mock_get, mock_config):
        """Test Ollama check when not running"""
        from core.health_monitor import HealthMonitor

        mock_get.side_effect = Exception("Connection refused")

        monitor = HealthMonitor()
        result = monitor.check_ollama()

        assert result["running"] is False
        assert result["status"] == "🔴"
        assert "error" in result

    def test_overall_status_all_good(self, mock_config):
        """Test overall status when all systems good"""
        from core.health_monitor import HealthMonitor

        monitor = HealthMonitor()

        with patch.object(monitor, "check_ram") as mock_ram:
            with patch.object(monitor, "check_disk") as mock_disk:
                with patch.object(monitor, "check_ollama") as mock_ollama:
                    mock_ram.return_value = {"percent": 50, "warning": False}
                    mock_disk.return_value = {"free_gb": 100, "warning": False}
                    mock_ollama.return_value = {"running": True}

                    status = monitor._overall_status()

                    assert "ALL SYSTEMS GO" in status

    def test_overall_status_ollama_down(self, mock_config):
        """Test overall status when Ollama is down"""
        from core.health_monitor import HealthMonitor

        monitor = HealthMonitor()

        with patch.object(monitor, "check_ram") as mock_ram:
            with patch.object(monitor, "check_disk") as mock_disk:
                with patch.object(monitor, "check_ollama") as mock_ollama:
                    mock_ram.return_value = {"percent": 50, "warning": False}
                    mock_disk.return_value = {"free_gb": 100, "warning": False}
                    mock_ollama.return_value = {"running": False}

                    status = monitor._overall_status()

                    assert "OLLAMA DOWN" in status

    def test_check_all(self, mock_config):
        """Test check_all returns all health checks"""
        from core.health_monitor import HealthMonitor

        monitor = HealthMonitor()

        with patch.object(monitor, "check_ram") as mock_ram:
            with patch.object(monitor, "check_disk") as mock_disk:
                with patch.object(monitor, "check_ollama") as mock_ollama:
                    with patch.object(monitor, "_overall_status") as mock_overall:
                        mock_ram.return_value = {"percent": 50, "warning": False}
                        mock_disk.return_value = {"free_gb": 100, "warning": False}
                        mock_ollama.return_value = {"running": True}
                        mock_overall.return_value = "🟢 ALL SYSTEMS GO"

                        result = monitor.check_all()

                        assert "ram" in result
                        assert "disk" in result
                        assert "ollama" in result
                        assert "overall" in result
