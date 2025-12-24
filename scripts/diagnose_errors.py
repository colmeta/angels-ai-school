"""
Automated Error Diagnostic Script
Analyzes current errors and suggests fixes
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.services.error_analyzer import get_error_analyzer, ErrorAnalysis


async def diagnose_google_signin_error():
    """Diagnose Google signin 400 error"""
    
    print("\n" + "="*60)
    print("🔍 DIAGNOSING: Google Signin Error 400")
    print("="*60 + "\n")
    
    analyzer = get_error_analyzer()
    
    # Analyze the error
    analysis = await analyzer.analyze_error(
        error_type="HTTP400Error",
        error_message="Google signin returned error 400",
        stack_trace="Unknown - need to capture from logs",
        context={
            "endpoint": "/api/auth/google",
            "user_action": "Attempting Google OAuth signin",
            "expected": "Successful authentication",
            "actual": "HTTP 400 Bad Request"
        }
    )
    
    # Display analysis
    print(f"📋 Error Category: {analysis.category.value}")
    print(f"⚠️  Severity: {analysis.severity.value}")
    print(f"🎯 Confidence: {analysis.confidence_score:.0%}")
    print(f"\n💡 Suggested Fix:\n{analysis.suggested_fix}")
    print(f"\n🔧 Auto-fix Recommended: {'Yes' if analyzer.should_auto_fix(analysis) else 'No (manual review required)'}")
    
    return analysis


async def diagnose_ai_core_download_error():
    """Diagnose AI core engine download failure"""
    
    print("\n" + "="*60)
    print("🔍 DIAGNOSING: AI Core Engine Download Failure")
    print("="*60 + "\n")
    
    analyzer = get_error_analyzer()
    
    # Analyze the error
    analysis = await analyzer.analyze_error(
        error_type="DownloadError",
        error_message="Download the core AI showed engine failed",
        stack_trace="Unknown - need to capture from logs",
        context={
            "component": "AI Core Engine",
            "action": "Downloading engine/model",
            "expected": "Successful download",
            "actual": "Download failure"
        }
    )
    
    # Display analysis
    print(f"📋 Error Category: {analysis.category.value}")
    print(f"⚠️  Severity: {analysis.severity.value}")
    print(f"🎯 Confidence: {analysis.confidence_score:.0%}")
    print(f"\n💡 Suggested Fix:\n{analysis.suggested_fix}")
    print(f"\n🔧 Auto-fix Recommended: {'Yes' if analyzer.should_auto_fix(analysis) else 'No (manual review required)'}")
    
    return analysis


async def main():
    """Main diagnostic routine"""
    
    print("\n" + "🤖 AUTONOMOUS ERROR DETECTION & REPAIR SYSTEM".center(60, "="))
    print("Starting automated diagnostic session...\n")
    
    # Diagnose both errors
    google_analysis = await diagnose_google_signin_error()
    ai_core_analysis = await diagnose_ai_core_download_error()
    
    # Summary
    print("\n" + "="*60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*60)
    print(f"\nTotal Errors Analyzed: 2")
    print(f"Critical Issues: {sum(1 for a in [google_analysis, ai_core_analysis] if a.severity.value == 'critical')}")
    print(f"High Priority: {sum(1 for a in [google_analysis, ai_core_analysis] if a.severity.value == 'high')}")
    print(f"Auto-fixable: {sum(1 for a in [google_analysis, ai_core_analysis] if get_error_analyzer().should_auto_fix(a))}")
    
    print("\n" + "="*60)
    print("✅ Diagnostic session complete")
    print("="*60 + "\n")
    
    print("Next steps:")
    print("1. Review suggested fixes above")
    print("2. Check detailed logs for stack traces")
    print("3. Apply fixes (auto or manual)")
    print("4. Run validation tests")


if __name__ == "__main__":
    asyncio.run(main())
