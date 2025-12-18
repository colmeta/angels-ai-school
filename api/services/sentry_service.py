"""
Sentry Error Monitoring Integration
Tracks errors, performance, and user sessions
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
import os

def init_sentry():
    """Initialize Sentry error monitoring"""
    sentry_dsn = os.getenv('SENTRY_DSN')
    environment = os.getenv('ENVIRONMENT', 'development')
    
    if not sentry_dsn:
        print("⚠️  Sentry DSN not configured - error monitoring disabled")
        return
    
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        
        # Integrations
        integrations=[
            FastApiIntegration(
                transaction_style="url",
                failed_request_status_codes=[500, 502, 503, 504]
            ),
            SqlalchemyIntegration(),
        ],
        
        # Performance monitoring
        traces_sample_rate=1.0 if environment == 'development' else 0.1,
        
        # Session tracking
        session_mode="application",
        
        # Release tracking
        release=os.getenv('RELEASE_VERSION', 'dev'),
        
        # Custom filters
        before_send=filter_sensitive_data,
        before_breadcrumb=filter_sensitive_breadcrumbs,
    )
    
    print(f"✅ Sentry initialized (environment: {environment})")


def filter_sensitive_data(event, hint):
    """Remove sensitive data from error reports"""
    # Remove passwords, tokens, API keys
    if 'request' in event:
        request = event['request']
        
        # Remove sensitive headers
        if 'headers' in request:
            sensitive_headers = ['authorization', 'api-key', 'x-api-key', 'cookie']
            for header in sensitive_headers:
                if header in request['headers']:
                    request['headers'][header] = '[REDACTED]'
        
        # Remove sensitive query params
        if 'query_string' in request:
            sensitive_params = ['password', 'token', 'api_key', 'secret']
            for param in sensitive_params:
                if param in request['query_string'].lower():
                    request['query_string'] = '[REDACTED]'
        
        # Remove sensitive post data
        if 'data' in request:
            if isinstance(request['data'], dict):
                for key in ['password', 'token', 'api_key', 'secret']:
                    if key in request['data']:
                        request['data'][key] = '[REDACTED]'
    
    return event


def filter_sensitive_breadcrumbs(crumb, hint):
    """Remove sensitive data from breadcrumbs"""
    if crumb.get('category') == 'query':
        # Redact SQL queries that might contain sensitive data
        if 'message' in crumb:
            if any(word in crumb['message'].lower() for word in ['password', 'token', 'secret']):
                crumb['message'] = '[REDACTED SQL QUERY]'
    
    return crumb


def capture_exception(error, context=None):
    """Manually capture an exception with context"""
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_context(key, value)
            sentry_sdk.capture_exception(error)
    else:
        sentry_sdk.capture_exception(error)


def capture_message(message, level='info', context=None):
    """Capture a custom message"""
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_context(key, value)
            sentry_sdk.capture_message(message, level=level)
    else:
        sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id, email=None, school_id=None):
    """Set user context for error tracking"""
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "school_id": school_id
    })
