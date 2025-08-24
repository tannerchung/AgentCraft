#!/usr/bin/env python3
"""
Comprehensive webhook test scenarios for AgentCraft
Tests real-world webhook integration patterns and failure modes
"""

import json
import hmac
import hashlib
import time
import asyncio
import aiohttp
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class WebhookEventType(Enum):
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    ORDER_PLACED = "order.placed"
    PAYMENT_SUCCESS = "payment.success"
    PAYMENT_FAILED = "payment.failed"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    SYSTEM_ALERT = "system.alert"


@dataclass
class WebhookTestScenario:
    name: str
    event_type: WebhookEventType
    payload: Dict[str, Any]
    expected_response: int
    headers: Optional[Dict[str, str]] = None
    auth_required: bool = False
    simulate_delay: float = 0.0
    should_retry: bool = False


class WebhookTestSuite:
    def __init__(self, base_url: str = "http://localhost:8000", secret_key: str = "test_secret_123"):
        self.base_url = base_url
        self.secret_key = secret_key
        self.test_results: List[Dict] = []
        
    def generate_signature(self, payload: str) -> str:
        """Generate HMAC SHA256 signature for webhook payload"""
        return hmac.new(
            self.secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def create_realistic_scenarios(self) -> List[WebhookTestScenario]:
        """Create realistic webhook test scenarios"""
        scenarios = []
        
        # 1. Successful user creation webhook
        scenarios.append(WebhookTestScenario(
            name="successful_user_creation",
            event_type=WebhookEventType.USER_CREATED,
            payload={
                "event_id": "evt_7h3k2j9m8n4p",
                "event_type": "user.created",
                "timestamp": datetime.utcnow().isoformat(),
                "api_version": "2024-01-01",
                "data": {
                    "object": "user",
                    "id": "usr_4k7j2h9m3n8p",
                    "email": "john.doe@example.com",
                    "name": "John Doe",
                    "created_at": datetime.utcnow().isoformat(),
                    "subscription_tier": "premium",
                    "metadata": {
                        "source": "web_signup",
                        "utm_campaign": "spring_2024",
                        "referral_code": "FRIEND123"
                    }
                },
                "previous_attributes": None
            },
            expected_response=200,
            auth_required=True
        ))
        
        # 2. E-commerce order placement
        scenarios.append(WebhookTestScenario(
            name="ecommerce_order_placed",
            event_type=WebhookEventType.ORDER_PLACED,
            payload={
                "event_id": "evt_9m5k3j2n7p4q",
                "event_type": "order.placed",
                "timestamp": datetime.utcnow().isoformat(),
                "api_version": "2024-01-01",
                "data": {
                    "object": "order",
                    "id": "ord_8n4k7j2m9p5q",
                    "customer_id": "cus_5j8k2n7m4p9q",
                    "status": "pending_payment",
                    "amount": 15999,  # $159.99 in cents
                    "currency": "usd",
                    "items": [
                        {
                            "id": "item_2n8k5j7m3p6q",
                            "product_id": "prod_wireless_headphones",
                            "name": "Wireless Bluetooth Headphones",
                            "quantity": 1,
                            "unit_price": 15999,
                            "total": 15999
                        }
                    ],
                    "shipping_address": {
                        "name": "Jane Smith",
                        "line1": "123 Main Street",
                        "line2": "Apt 4B",
                        "city": "New York",
                        "state": "NY",
                        "postal_code": "10001",
                        "country": "US"
                    },
                    "metadata": {
                        "channel": "web",
                        "device_type": "desktop",
                        "campaign_id": "summer_sale_2024"
                    }
                }
            },
            expected_response=200,
            auth_required=True
        ))
        
        # 3. Payment failure scenario
        scenarios.append(WebhookTestScenario(
            name="payment_failure_scenario",
            event_type=WebhookEventType.PAYMENT_FAILED,
            payload={
                "event_id": "evt_4p7k5j8n2m9q",
                "event_type": "payment.failed",
                "timestamp": datetime.utcnow().isoformat(),
                "api_version": "2024-01-01",
                "data": {
                    "object": "payment",
                    "id": "pay_3n7k4j9m5p8q",
                    "order_id": "ord_8n4k7j2m9p5q",
                    "customer_id": "cus_5j8k2n7m4p9q",
                    "amount": 15999,
                    "currency": "usd",
                    "status": "failed",
                    "failure_reason": "insufficient_funds",
                    "failure_code": "card_declined",
                    "failure_message": "Your card was declined. Please try a different payment method.",
                    "payment_method": {
                        "type": "card",
                        "card": {
                            "brand": "visa",
                            "last4": "4242",
                            "exp_month": 12,
                            "exp_year": 2025
                        }
                    },
                    "retry_count": 2,
                    "next_retry_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
                }
            },
            expected_response=200,
            auth_required=True,
            should_retry=True
        ))
        
        # 4. System alert webhook
        scenarios.append(WebhookTestScenario(
            name="system_alert_high_priority",
            event_type=WebhookEventType.SYSTEM_ALERT,
            payload={
                "event_id": "evt_alert_9k2j5n8m7p3q",
                "event_type": "system.alert",
                "timestamp": datetime.utcnow().isoformat(),
                "api_version": "2024-01-01",
                "data": {
                    "object": "alert",
                    "id": "alert_cpu_spike_2024",
                    "severity": "high",
                    "alert_type": "infrastructure",
                    "service": "api-server",
                    "message": "CPU usage exceeded 90% threshold",
                    "metrics": {
                        "cpu_usage_percent": 94.7,
                        "memory_usage_mb": 2847,
                        "disk_usage_percent": 67.3,
                        "active_connections": 1247
                    },
                    "affected_regions": ["us-east-1", "us-west-2"],
                    "started_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                    "escalation_level": 2,
                    "on_call_engineer": "sarah.wilson@company.com"
                }
            },
            expected_response=200,
            auth_required=True,
            simulate_delay=0.1  # Slight delay to simulate processing
        ))
        
        # 5. Large payload scenario (testing limits)
        large_metadata = {f"custom_field_{i}": f"value_{i}" * 50 for i in range(100)}
        scenarios.append(WebhookTestScenario(
            name="large_payload_test",
            event_type=WebhookEventType.USER_UPDATED,
            payload={
                "event_id": "evt_large_payload_test",
                "event_type": "user.updated",
                "timestamp": datetime.utcnow().isoformat(),
                "api_version": "2024-01-01",
                "data": {
                    "object": "user",
                    "id": "usr_large_update_test",
                    "metadata": large_metadata,
                    "change_log": [f"Field {i} updated" for i in range(50)]
                }
            },
            expected_response=200,
            auth_required=True
        ))
        
        # 6. Subscription cancellation with prorated refund
        scenarios.append(WebhookTestScenario(
            name="subscription_cancellation_refund",
            event_type=WebhookEventType.SUBSCRIPTION_CANCELLED,
            payload={
                "event_id": "evt_sub_cancel_2024",
                "event_type": "subscription.cancelled",
                "timestamp": datetime.utcnow().isoformat(),
                "api_version": "2024-01-01",
                "data": {
                    "object": "subscription",
                    "id": "sub_premium_monthly_789",
                    "customer_id": "cus_5j8k2n7m4p9q",
                    "plan": {
                        "id": "premium_monthly",
                        "name": "Premium Monthly",
                        "amount": 2999,  # $29.99
                        "currency": "usd",
                        "interval": "month"
                    },
                    "status": "cancelled",
                    "cancelled_at": datetime.utcnow().isoformat(),
                    "cancellation_reason": "customer_request",
                    "cancellation_feedback": "Switching to annual plan",
                    "current_period_start": (datetime.utcnow() - timedelta(days=15)).isoformat(),
                    "current_period_end": (datetime.utcnow() + timedelta(days=15)).isoformat(),
                    "proration_details": {
                        "days_used": 15,
                        "days_total": 30,
                        "refund_amount": 1499,  # $14.99 prorated refund
                        "refund_currency": "usd"
                    }
                }
            },
            expected_response=200,
            auth_required=True
        ))
        
        return scenarios
    
    def create_failure_scenarios(self) -> List[WebhookTestScenario]:
        """Create scenarios that test failure modes and edge cases"""
        failure_scenarios = []
        
        # 1. Invalid JSON payload
        failure_scenarios.append(WebhookTestScenario(
            name="invalid_json_payload",
            event_type=WebhookEventType.USER_CREATED,
            payload={"incomplete": "json", "missing_closing_brace": True},  # Will be malformed in transmission
            expected_response=400
        ))
        
        # 2. Missing required fields
        failure_scenarios.append(WebhookTestScenario(
            name="missing_required_fields",
            event_type=WebhookEventType.ORDER_PLACED,
            payload={
                "event_type": "order.placed",
                # Missing event_id, timestamp, data
            },
            expected_response=400
        ))
        
        # 3. Invalid signature
        failure_scenarios.append(WebhookTestScenario(
            name="invalid_signature_auth",
            event_type=WebhookEventType.PAYMENT_SUCCESS,
            payload={
                "event_id": "evt_invalid_sig_test",
                "event_type": "payment.success",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {"amount": 1000}
            },
            expected_response=401,
            auth_required=True,
            headers={"X-Webhook-Signature": "sha256=invalid_signature_here"}
        ))
        
        return failure_scenarios
    
    async def send_webhook_async(self, scenario: WebhookTestScenario, endpoint: str) -> Dict[str, Any]:
        """Send webhook asynchronously with proper error handling"""
        if scenario.simulate_delay > 0:
            await asyncio.sleep(scenario.simulate_delay)
        
        # Special handling for invalid JSON scenario
        if scenario.name == "invalid_json_payload":
            payload_json = '{"incomplete": "json", "missing_closing_brace": true'  # Deliberately malformed
        else:
            payload_json = json.dumps(scenario.payload, sort_keys=True)
        
        headers = {
            "Content-Type": "application/json",
            "X-Event-Type": scenario.event_type.value,
            "User-Agent": "AgentCraft-Webhook-Test/1.0"
        }
        
        if scenario.auth_required:
            signature = self.generate_signature(payload_json)
            headers["X-Webhook-Signature"] = f"sha256={signature}"
        
        if scenario.headers:
            headers.update(scenario.headers)
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    endpoint,
                    data=payload_json,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_time = time.time() - start_time
                    response_text = await response.text()
                    
                    return {
                        "scenario": scenario.name,
                        "status_code": response.status,
                        "response_time": response_time,
                        "success": response.status == scenario.expected_response,
                        "response_body": response_text[:500],  # Truncate long responses
                        "headers": dict(response.headers)
                    }
                    
            except asyncio.TimeoutError:
                return {
                    "scenario": scenario.name,
                    "status_code": None,
                    "response_time": time.time() - start_time,
                    "success": False,
                    "error": "Request timeout",
                    "response_body": ""
                }
            except Exception as e:
                return {
                    "scenario": scenario.name,
                    "status_code": None,
                    "response_time": time.time() - start_time,
                    "success": False,
                    "error": str(e),
                    "response_body": ""
                }
    
    def send_webhook_sync(self, scenario: WebhookTestScenario, endpoint: str) -> Dict[str, Any]:
        """Send webhook synchronously for simple testing"""
        if scenario.simulate_delay > 0:
            time.sleep(scenario.simulate_delay)
        
        # Special handling for invalid JSON scenario
        if scenario.name == "invalid_json_payload":
            payload_json = '{"incomplete": "json", "missing_closing_brace": true'  # Deliberately malformed
        else:
            payload_json = json.dumps(scenario.payload, sort_keys=True)
        
        headers = {
            "Content-Type": "application/json",
            "X-Event-Type": scenario.event_type.value,
            "User-Agent": "AgentCraft-Webhook-Test/1.0"
        }
        
        if scenario.auth_required:
            signature = self.generate_signature(payload_json)
            headers["X-Webhook-Signature"] = f"sha256={signature}"
        
        if scenario.headers:
            headers.update(scenario.headers)
        
        start_time = time.time()
        
        try:
            response = requests.post(
                endpoint,
                data=payload_json,
                headers=headers,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            return {
                "scenario": scenario.name,
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code == scenario.expected_response,
                "response_body": response.text[:500],
                "headers": dict(response.headers)
            }
            
        except requests.exceptions.Timeout:
            return {
                "scenario": scenario.name,
                "status_code": None,
                "response_time": time.time() - start_time,
                "success": False,
                "error": "Request timeout",
                "response_body": ""
            }
        except Exception as e:
            return {
                "scenario": scenario.name,
                "status_code": None,
                "response_time": time.time() - start_time,
                "success": False,
                "error": str(e),
                "response_body": ""
            }
    
    async def run_async_test_suite(self, webhook_endpoint: str) -> Dict[str, Any]:
        """Run all webhook tests asynchronously"""
        print("🚀 Starting comprehensive webhook test suite...")
        
        all_scenarios = self.create_realistic_scenarios() + self.create_failure_scenarios()
        
        # Run all scenarios concurrently
        tasks = []
        for scenario in all_scenarios:
            task = self.send_webhook_async(scenario, webhook_endpoint)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        passed = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))
        total = len(results)
        
        test_summary = {
            "total_scenarios": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed / total) * 100 if total > 0 else 0,
            "results": [r for r in results if isinstance(r, dict)],
            "errors": [r for r in results if not isinstance(r, dict)]
        }
        
        return test_summary
    
    def run_sync_test_suite(self, webhook_endpoint: str) -> Dict[str, Any]:
        """Run webhook tests synchronously"""
        print("🚀 Starting webhook test suite (synchronous)...")
        
        realistic_scenarios = self.create_realistic_scenarios()
        failure_scenarios = self.create_failure_scenarios()
        
        all_results = []
        
        # Test realistic scenarios
        print("\n📋 Testing realistic webhook scenarios...")
        for scenario in realistic_scenarios:
            print(f"  Testing: {scenario.name}")
            result = self.send_webhook_sync(scenario, webhook_endpoint)
            all_results.append(result)
            
            status_icon = "✅" if result['success'] else "❌"
            print(f"    {status_icon} Status: {result['status_code']} | Time: {result['response_time']:.3f}s")
        
        # Test failure scenarios
        print("\n⚠️  Testing failure scenarios...")
        for scenario in failure_scenarios:
            print(f"  Testing: {scenario.name}")
            result = self.send_webhook_sync(scenario, webhook_endpoint)
            all_results.append(result)
            
            status_icon = "✅" if result['success'] else "❌"
            print(f"    {status_icon} Status: {result['status_code']} | Time: {result['response_time']:.3f}s")
        
        # Calculate summary
        passed = sum(1 for r in all_results if r.get('success', False))
        total = len(all_results)
        
        return {
            "total_scenarios": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed / total) * 100 if total > 0 else 0,
            "results": all_results
        }


def main():
    """Main function to run webhook tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AgentCraft Webhook Test Suite")
    parser.add_argument("--endpoint", default="http://localhost:8000/webhooks/receive", 
                       help="Webhook endpoint URL to test")
    parser.add_argument("--async-mode", action="store_true", 
                       help="Run tests asynchronously")
    parser.add_argument("--secret", default="test_secret_123", 
                       help="Secret key for webhook signatures")
    
    args = parser.parse_args()
    
    test_suite = WebhookTestSuite(secret_key=args.secret)
    
    print("🔧 AgentCraft Webhook Test Suite")
    print("=" * 50)
    print(f"Endpoint: {args.endpoint}")
    print(f"Mode: {'Async' if args.async_mode else 'Sync'}")
    print(f"Secret Key: {args.secret[:8]}...")
    print()
    
    if args.async_mode:
        # Run async tests
        results = asyncio.run(test_suite.run_async_test_suite(args.endpoint))
    else:
        # Run sync tests
        results = test_suite.run_sync_test_suite(args.endpoint)
    
    # Print summary
    print(f"\n📊 Test Results Summary")
    print(f"Total Scenarios: {results['total_scenarios']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    
    # Print failed scenarios
    failed_results = [r for r in results['results'] if not r.get('success', False)]
    if failed_results:
        print(f"\n❌ Failed Scenarios:")
        for result in failed_results:
            status_code = result.get('status_code', 'Unknown')
            error_msg = result.get('error', f'Status {status_code}')
            print(f"  - {result['scenario']}: {error_msg}")
    
    if results['success_rate'] == 100:
        print("\n🎉 All webhook scenarios passed!")
    elif results['success_rate'] >= 80:
        print("\n✅ Most webhook scenarios passed - good coverage!")
    else:
        print("\n⚠️  Multiple webhook scenarios failed - review implementation")


if __name__ == "__main__":
    main()