"""
Navigation Health Check API
Provides real-time navigation system status
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from business.navigation_validator import NavigationValidator
import json

@csrf_exempt
@require_http_methods(["GET", "POST"])
def navigation_health_check(request):
    """
    API endpoint for navigation health check
    GET: Returns current navigation status
    POST: Runs full navigation validation
    """
    
    if request.method == 'GET':
        # Quick status check
        try:
            from django.urls import reverse
            from business import views
            
            # Check critical navigation URLs
            critical_urls = ['dashboard', 'orders', 'inventory', 'customer_list']
            status = {
                'status': 'healthy',
                'checks': {},
                'timestamp': None
            }
            
            for url_name in critical_urls:
                try:
                    reverse(url_name)
                    status['checks'][url_name] = 'ok'
                except Exception as e:
                    status['checks'][url_name] = f'error: {str(e)}'
                    status['status'] = 'unhealthy'
            
            return JsonResponse(status)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'timestamp': None
            }, status=500)
    
    elif request.method == 'POST':
        # Full validation
        try:
            validator = NavigationValidator()
            success = validator.validate_all_navigation()
            
            response_data = {
                'status': 'healthy' if success else 'unhealthy',
                'errors': validator.errors,
                'warnings': validator.warnings,
                'fixes_applied': validator.fixes_applied,
                'timestamp': None
            }
            
            status_code = 200 if success else 400
            return JsonResponse(response_data, status=status_code)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'timestamp': None
            }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def quick_nav_check(request):
    """
    Quick navigation check for monitoring
    Returns minimal status information
    """
    try:
        from django.urls import reverse
        
        # Test a few critical URLs
        test_urls = ['dashboard', 'orders', 'inventory']
        all_ok = True
        
        for url_name in test_urls:
            try:
                reverse(url_name)
            except:
                all_ok = False
                break
        
        return JsonResponse({
            'status': 'ok' if all_ok else 'error',
            'navigation': 'working' if all_ok else 'broken'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'navigation': 'broken',
            'error': str(e)
        }, status=500)
