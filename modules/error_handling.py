# error_handling.py - Comprehensive Error Handling and Health Monitoring
import functools
import traceback
import time
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str
    last_check: datetime
    response_time: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

class HealthMonitor:
    """Monitor system health and service availability"""
    
    def __init__(self):
        self.checks: Dict[str, HealthCheck] = {}
        self.error_counts: Dict[str, int] = {}
        self.last_errors: Dict[str, str] = {}
        
    def check_ollama_health(self) -> HealthCheck:
        """Check if Ollama service is available"""
        start_time = time.time()
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                return HealthCheck(
                    name="ollama",
                    status=HealthStatus.HEALTHY,
                    message=f"Ollama running with {len(models)} models",
                    last_check=datetime.now(),
                    response_time=response_time,
                    details={"models": [m.get('name', 'unknown') for m in models]}
                )
            else:
                return HealthCheck(
                    name="ollama",
                    status=HealthStatus.WARNING,
                    message=f"Ollama responded with status {response.status_code}",
                    last_check=datetime.now(),
                    response_time=response_time
                )
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheck(
                name="ollama",
                status=HealthStatus.CRITICAL,
                message=f"Ollama unavailable: {str(e)}",
                last_check=datetime.now(),
                response_time=response_time
            )
    
    def check_deepgram_health(self, api_key: str) -> HealthCheck:
        """Check Deepgram API availability"""
        if not api_key:
            return HealthCheck(
                name="deepgram",
                status=HealthStatus.WARNING,
                message="No API key configured",
                last_check=datetime.now()
            )
        
        start_time = time.time()
        try:
            headers = {"Authorization": f"Token {api_key}"}
            response = requests.get("https://api.deepgram.com/v1/projects", 
                                  headers=headers, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return HealthCheck(
                    name="deepgram",
                    status=HealthStatus.HEALTHY,
                    message="Deepgram API accessible",
                    last_check=datetime.now(),
                    response_time=response_time
                )
            else:
                return HealthCheck(
                    name="deepgram",
                    status=HealthStatus.WARNING,
                    message=f"Deepgram API returned {response.status_code}",
                    last_check=datetime.now(),
                    response_time=response_time
                )
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheck(
                name="deepgram",
                status=HealthStatus.CRITICAL,
                message=f"Deepgram unavailable: {str(e)}",
                last_check=datetime.now(),
                response_time=response_time
            )
    
    def check_system_resources(self) -> HealthCheck:
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            if cpu_percent > 80:
                status = HealthStatus.WARNING
                warnings.append(f"High CPU usage: {cpu_percent}%")
            
            if memory.percent > 85:
                status = HealthStatus.WARNING
                warnings.append(f"High memory usage: {memory.percent}%")
            
            if disk.percent > 90:
                status = HealthStatus.CRITICAL
                warnings.append(f"Low disk space: {disk.percent}% used")
            
            message = "System resources OK" if not warnings else "; ".join(warnings)
            
            return HealthCheck(
                name="system",
                status=status,
                message=message,
                last_check=datetime.now(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "disk_percent": disk.percent,
                    "disk_free_gb": round(disk.free / (1024**3), 2)
                }
            )
        except Exception as e:
            return HealthCheck(
                name="system",
                status=HealthStatus.CRITICAL,
                message=f"Cannot check system resources: {str(e)}",
                last_check=datetime.now()
            )
    
    def run_all_checks(self, deepgram_api_key: str = "") -> Dict[str, HealthCheck]:
        """Run all health checks"""
        self.checks["ollama"] = self.check_ollama_health()
        self.checks["deepgram"] = self.check_deepgram_health(deepgram_api_key)
        self.checks["system"] = self.check_system_resources()
        return self.checks
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status"""
        if not self.checks:
            return HealthStatus.UNKNOWN
        
        statuses = [check.status for check in self.checks.values()]
        
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    def record_error(self, component: str, error: str):
        """Record an error for a component"""
        self.error_counts[component] = self.error_counts.get(component, 0) + 1
        self.last_errors[component] = error
    
    def get_error_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of errors by component"""
        return {
            component: {
                "count": count,
                "last_error": self.last_errors.get(component, ""),
                "error_rate": count / max(1, (datetime.now() - datetime.now().replace(hour=0, minute=0, second=0)).seconds / 3600)
            }
            for component, count in self.error_counts.items()
        }

# Global health monitor instance
health_monitor = HealthMonitor()

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retrying functions on failure"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    component = func.__module__ + "." + func.__name__
                    health_monitor.record_error(component, str(e))
                    
                    if attempt < max_retries:
                        sleep_time = delay * (backoff ** attempt)
                        print(f"⚠️ {component} failed (attempt {attempt + 1}/{max_retries + 1}). "
                              f"Retrying in {sleep_time:.1f}s...")
                        time.sleep(sleep_time)
                    else:
                        print(f"❌ {component} failed after {max_retries + 1} attempts")
            
            raise last_exception
        return wrapper
    return decorator

def handle_exceptions(component: str = None, fallback_value: Any = None, 
                     log_errors: bool = True):
    """Decorator for graceful exception handling"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                comp_name = component or f"{func.__module__}.{func.__name__}"
                error_msg = f"{comp_name}: {str(e)}"
                
                if log_errors:
                    print(f"❌ Error in {error_msg}")
                    print(f"📊 Traceback: {traceback.format_exc()}")
                
                health_monitor.record_error(comp_name, str(e))
                
                if fallback_value is not None:
                    print(f"🔄 Using fallback value for {comp_name}")
                    return fallback_value
                
                raise
        return wrapper
    return decorator

def circuit_breaker(failure_threshold: int = 5, timeout: int = 60):
    """Circuit breaker pattern implementation"""
    def decorator(func: Callable) -> Callable:
        func._failures = 0
        func._last_failure_time = None
        func._state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Check if circuit should be half-open
            if (func._state == "OPEN" and 
                func._last_failure_time and 
                now - func._last_failure_time > timeout):
                func._state = "HALF_OPEN"
                print(f"🔄 Circuit breaker for {func.__name__} is now HALF_OPEN")
            
            # If circuit is open, fail fast
            if func._state == "OPEN":
                raise Exception(f"Circuit breaker OPEN for {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                # Success - reset circuit breaker
                if func._state == "HALF_OPEN":
                    func._state = "CLOSED"
                    func._failures = 0
                    print(f"✅ Circuit breaker for {func.__name__} is now CLOSED")
                return result
            except Exception as e:
                func._failures += 1
                func._last_failure_time = now
                
                if func._failures >= failure_threshold:
                    func._state = "OPEN"
                    print(f"🔴 Circuit breaker for {func.__name__} is now OPEN")
                
                raise
        return wrapper
    return decorator

# Health check CLI command
def print_health_report(deepgram_api_key: str = ""):
    """Print a comprehensive health report"""
    print("🏥 JARVIS HEALTH REPORT")
    print("=" * 50)
    
    checks = health_monitor.run_all_checks(deepgram_api_key)
    overall_status = health_monitor.get_overall_status()
    
    # Overall status
    status_emoji = {
        HealthStatus.HEALTHY: "✅",
        HealthStatus.WARNING: "⚠️",
        HealthStatus.CRITICAL: "🔴",
        HealthStatus.UNKNOWN: "❓"
    }
    
    print(f"Overall Status: {status_emoji[overall_status]} {overall_status.value.upper()}")
    print()
    
    # Individual checks
    for name, check in checks.items():
        emoji = status_emoji[check.status]
        print(f"{emoji} {name.upper()}: {check.message}")
        if check.response_time > 0:
            print(f"   Response time: {check.response_time:.2f}s")
        if check.details:
            for key, value in check.details.items():
                print(f"   {key}: {value}")
        print()
    
    # Error summary
    error_summary = health_monitor.get_error_summary()
    if error_summary:
        print("📊 ERROR SUMMARY")
        print("-" * 30)
        for component, info in error_summary.items():
            print(f"{component}: {info['count']} errors (rate: {info['error_rate']:.2f}/hour)")
            if info['last_error']:
                print(f"   Last error: {info['last_error']}")
        print()

if __name__ == "__main__":
    print_health_report()
