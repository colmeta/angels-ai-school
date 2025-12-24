"""
Health Monitor Script
Continuous monitoring of all API endpoints and system health
"""
import requests
import time
from typing import List, Dict, Tuple
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class HealthMonitor:
    """Monitor health of all services and endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict] = []
    
    def check_endpoint(self, method: str, path: str, expected_status: List[int] = None) -> Tuple[bool, int, str]:
        """Check if endpoint is accessible"""
        
        if expected_status is None:
            expected_status = [200, 401, 403]  # Default acceptable statuses
        
        try:
            url = f"{self.base_url}{path}"
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=5)
            elif method.upper() == "POST":
                response = requests.post(url, json={}, timeout=5)
            else:
                return False, 0, f"Unsupported method: {method}"
            
            status_ok = response.status_code in expected_status
            
            return status_ok, response.status_code, "OK" if status_ok else "Unexpected status code"
            
        except requests.exceptions.Timeout:
            return False, 0, "Timeout"
        except requests.exceptions.ConnectionError:
            return False, 0, "Connection refused"
        except Exception as e:
            return False, 0, str(e)
    
    def run_health_checks(self) -> Dict:
        """Run comprehensive health checks"""
        
        print(f"\\n{'='*60}")
        print(f"Health Check Started: {datetime.now().isoformat()}")
        print(f"Base URL: {self.base_url}")
        print(f"{'='*60}\\n")
        
        endpoints_to_check = [
            # Core endpoints
            ("GET", "/", [200]),
            ("GET", "/api/health", [200]),
            ("GET", "/docs", [200]),
            
            # Authentication (should require auth or return 401)
            ("GET", "/api/students", [200, 401, 403, 404]),
            ("GET", "/api/fees", [200, 401, 403, 404]),
            ("GET", "/api/teachers", [200, 401, 403, 404]),
            
            # AI Agents
            ("GET", "/api/v1/agents/digital-ceo", [200, 401, 403, 404]),
            ("GET", "/api/v1/clarity", [200, 401, 403, 404, 405]),
            
            # School registration (should accept POST)
            ("POST", "/api/schools/register", [200, 400, 422]),
            
            # Analytics
            ("GET", "/api/analytics/dashboard", [200, 401, 403, 404]),
            
            # Feature flags
            ("GET", "/api/v1/experiments/list", [200, 401, 403, 404]),
        ]
        
        results = []
        success_count = 0
        failure_count = 0
        
        for method, path, expected_statuses in endpoints_to_check:
            status_ok, status_code, message = self.check_endpoint(method, path, expected_statuses)
            
            result = {
                "method": method,
                "path": path,
                "status_code": status_code,
                "status_ok": status_ok,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(result)
            
            # Print result
            status_icon = "✓" if status_ok else "✗"
            status_color = "\\033[92m" if status_ok else "\\033[91m"
            reset_color = "\\033[0m"
            
            print(f"{status_color}{status_icon}{reset_color} {method:6} {path:40} [{status_code}] {message}")
            
            if status_ok:
                success_count += 1
            else:
                failure_count += 1
        
        # Summary
        total = len(results)
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        print(f"\\n{'='*60}")
        print(f"Health Check Summary")
        print(f"{'='*60}")
        print(f"Total Endpoints: {total}")
        print(f"✓ Passed: {success_count}")
        print(f"✗ Failed: {failure_count}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"{'='*60}\\n")
        
        return {
            "total": total,
            "success": success_count,
            "failure": failure_count,
            "success_rate": success_rate,
            "results": results
        }
    
    def continuous_monitor(self, interval_seconds: int = 300):
        """Run health checks continuously"""
        
        print(f"Starting continuous health monitoring (interval: {interval_seconds}s)")
        print("Press Ctrl+C to stop\\n")
        
        try:
            while True:
                summary = self.run_health_checks()
                
                # Alert if success rate drops below threshold
                if summary["success_rate"] < 80:
                    print("\\n⚠️  WARNING: Health check success rate below 80%!")
                    print("Consider investigating failed endpoints.\\n")
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\\nHealth monitoring stopped by user.")


def main():
    """Main entry point"""
    
    # Get base URL from environment or use default
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    monitor = HealthMonitor(base_url)
    
    # Check if continuous monitoring is requested
    if "--continuous" in sys.argv:
        interval = 300  # 5 minutes
        if "--interval" in sys.argv:
            try:
                idx = sys.argv.index("--interval")
                interval = int(sys.argv[idx + 1])
            except (IndexError, ValueError):
                print("Invalid interval value, using default (300s)")
        
        monitor.continuous_monitor(interval)
    else:
        # Run once
        monitor.run_health_checks()


if __name__ == "__main__":
    main()
