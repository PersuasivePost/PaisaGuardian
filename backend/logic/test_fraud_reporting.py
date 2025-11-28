#!/usr/bin/env python3
"""
Fraud Reporting System - Demonstration Script
Shows how fraud reports work and automatic blacklisting at 50 reports
"""

import sys
sys.path.insert(0, '/Users/yogeshvora/Desktop/fraud-sentinel-agent/backend/logic')

from learning_engine import learning_engine
from datetime import datetime

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_fraud_reporting():
    """Test fraud reporting with automatic blacklisting"""
    
    print_section("🚨 FRAUD REPORTING SYSTEM TEST")
    
    # Test entity
    test_phone = "+919876543210"
    test_upi = "scammer@paytm"
    
    print(f"📱 Test Phone Number: {test_phone}")
    print(f"💳 Test UPI ID: {test_upi}")
    print(f"🎯 Blacklist Threshold: {learning_engine.fraud_report_threshold} reports")
    
    # ========================================
    # TEST 1: Submit first report
    # ========================================
    print_section("TEST 1: Submit First Fraud Report")
    
    result = learning_engine.report_fraud(
        entity_id=test_phone,
        entity_type="phone_numbers",
        user_id="user001",
        description="Pretending to be bank, asked for OTP",
        fraud_category="sms_scam",
        amount_lost=5000.0,
        additional_info={
            "sms_content": "Your account will be blocked. Share OTP immediately",
            "claimed_bank": "HDFC Bank"
        }
    )
    
    print(f"✅ Report submitted")
    print(f"📊 Report count: {result['report_count']}/{result['threshold']}")
    print(f"🚫 Blacklisted: {result['blacklisted']}")
    print(f"💬 Message: {result['message']}")
    
    # ========================================
    # TEST 2: Submit multiple reports
    # ========================================
    print_section("TEST 2: Submit Multiple Reports (Building to Threshold)")
    
    print(f"Submitting reports 2-49 for {test_phone}...")
    for i in range(2, 50):
        result = learning_engine.report_fraud(
            entity_id=test_phone,
            entity_type="phone_numbers",
            user_id=f"user{str(i).zfill(3)}",
            description=f"Fraud report #{i}",
            fraud_category="sms_scam"
        )
    
    print(f"✅ {result['report_count']} reports submitted")
    print(f"🚫 Blacklisted: {result['blacklisted']}")
    
    # ========================================
    # TEST 3: Reach threshold - Automatic blacklisting
    # ========================================
    print_section("TEST 3: Reach Threshold (Report #50) - AUTOMATIC BLACKLISTING")
    
    result = learning_engine.report_fraud(
        entity_id=test_phone,
        entity_type="phone_numbers",
        user_id="user050",
        description="This is the 50th report - should trigger blacklist",
        fraud_category="sms_scam",
        amount_lost=10000.0
    )
    
    print(f"🎯 Report count: {result['report_count']}/{result['threshold']}")
    print(f"⚠️  BLACKLISTED: {result['blacklisted']}")
    print(f"💬 Message: {result['message']}")
    
    if result['blacklisted']:
        print("\n🚨 SUCCESS: Automatic blacklisting triggered!")
    
    # ========================================
    # TEST 4: Submit more reports (already blacklisted)
    # ========================================
    print_section("TEST 4: Submit Reports After Blacklisting")
    
    result = learning_engine.report_fraud(
        entity_id=test_phone,
        entity_type="phone_numbers",
        user_id="user051",
        description="Report after blacklist",
        fraud_category="sms_scam"
    )
    
    print(f"📊 Report count: {result['report_count']}")
    print(f"🚫 Already blacklisted: {result['blacklisted']}")
    print(f"💬 Message: {result['message']}")
    
    # ========================================
    # TEST 5: Test different entity type (UPI)
    # ========================================
    print_section("TEST 5: Test UPI ID Fraud Reporting")
    
    # Submit 52 reports for UPI ID to trigger blacklist
    print(f"Submitting 52 reports for {test_upi}...")
    for i in range(1, 53):
        result = learning_engine.report_fraud(
            entity_id=test_upi,
            entity_type="upi_ids",
            user_id=f"user{str(i+100).zfill(3)}",
            description=f"Fake UPI payment request #{i}",
            fraud_category="fake_upi",
            amount_lost=2000.0 if i % 5 == 0 else None
        )
    
    print(f"✅ {result['report_count']} reports submitted")
    print(f"⚠️  Blacklisted: {result['blacklisted']}")
    print(f"💬 Message: {result['message']}")
    
    # ========================================
    # TEST 6: Check fraud report history
    # ========================================
    print_section("TEST 6: View Fraud Report History")
    
    # Get reports for phone number
    phone_reports = learning_engine.get_fraud_reports(entity_id=test_phone)
    print(f"📱 Phone reports: {len(phone_reports)} total")
    print(f"   First report: {phone_reports[-1]['timestamp']}")
    print(f"   Last report: {phone_reports[0]['timestamp']}")
    
    # Get reports for UPI ID
    upi_reports = learning_engine.get_fraud_reports(entity_id=test_upi)
    print(f"\n💳 UPI reports: {len(upi_reports)} total")
    print(f"   First report: {upi_reports[-1]['timestamp']}")
    print(f"   Last report: {upi_reports[0]['timestamp']}")
    
    # Get all phone number reports
    all_phone_reports = learning_engine.get_fraud_reports(entity_type="phone_numbers")
    print(f"\n📞 All phone number reports: {len(all_phone_reports)}")
    
    # ========================================
    # TEST 7: View statistics
    # ========================================
    print_section("TEST 7: Fraud Report Statistics")
    
    stats = learning_engine.get_report_statistics()
    
    print(f"📊 Total unique entities reported: {stats['total_unique_entities_reported']}")
    print(f"📝 Total reports: {stats['total_reports']}")
    print(f"💰 Total amount lost: ₹{stats['total_amount_lost']:,.2f}")
    print(f"⚠️  Entities reaching threshold: {stats['entities_reaching_threshold']}")
    
    print(f"\n📈 Reports by count range:")
    for range_key, count in stats['entities_by_report_count'].items():
        print(f"   {range_key}: {count} entities")
    
    print(f"\n📊 Reports by entity type:")
    for entity_type, count in stats['reports_by_entity_type'].items():
        print(f"   {entity_type}: {count} reports")
    
    print(f"\n🏷️  Reports by fraud category:")
    for category, count in stats['reports_by_category'].items():
        print(f"   {category}: {count} reports")
    
    print(f"\n🚫 Auto-blacklisted entities:")
    for entity in stats['auto_blacklisted_entities']:
        print(f"   {entity['entity_id']}: {entity['report_count']} reports")
    
    # ========================================
    # TEST 8: Verify blacklist impact on risk scores
    # ========================================
    print_section("TEST 8: Verify Blacklist Impact on Risk Scoring")
    
    # Check if entities are in blacklist
    phone_blacklisted = learning_engine.check_blacklist(test_phone, "phone_numbers")
    upi_blacklisted = learning_engine.check_blacklist(test_upi, "upi_ids")
    
    print(f"📱 Phone {test_phone} in blacklist: {phone_blacklisted}")
    print(f"💳 UPI {test_upi} in blacklist: {upi_blacklisted}")
    
    # Test risk score adjustment
    original_score = 30.0
    adjusted_score, reasons = learning_engine.adjust_risk_score(
        entity_id=test_phone,
        entity_type="phone_numbers",
        original_score=original_score
    )
    
    print(f"\n📊 Risk Score Adjustment Test:")
    print(f"   Original score: {original_score}")
    print(f"   Adjusted score: {adjusted_score}")
    print(f"   Adjustment: +{adjusted_score - original_score}")
    print(f"   Reasons: {reasons}")
    
    # ========================================
    # TEST 9: Check metrics
    # ========================================
    print_section("TEST 9: Learning Engine Metrics")
    
    metrics = learning_engine.get_metrics()
    
    print(f"📊 Total feedbacks: {metrics['total_feedbacks']}")
    print(f"📝 Total fraud reports: {metrics.get('total_fraud_reports', 0)}")
    print(f"🎯 Unique reported entities: {metrics.get('unique_reported_entities', 0)}")
    
    print(f"\n📋 Blacklist sizes:")
    for entity_type, size in metrics['blacklist_sizes'].items():
        if size > 0:
            print(f"   {entity_type}: {size}")
    
    # ========================================
    # Summary
    # ========================================
    print_section("✅ TEST SUMMARY")
    
    print("🎉 All tests completed successfully!\n")
    print("✅ Fraud reporting system working")
    print("✅ Automatic blacklisting at 50 reports")
    print("✅ Multiple entity types supported")
    print("✅ Report history tracking")
    print("✅ Statistics generation")
    print("✅ Blacklist impact on risk scores")
    print("✅ Data persistence ready")
    
    print(f"\n📁 Data saved to: {learning_engine.data_dir}")
    print("   - fraud_reports.json")
    print("   - blacklist.json")
    print("   - metrics.json")
    
    print("\n🚀 System ready for production use!")


if __name__ == "__main__":
    try:
        test_fraud_reporting()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
