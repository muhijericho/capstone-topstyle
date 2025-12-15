def dark_mode_context(request):
    """Context processor to make dark_mode and system_settings available globally"""
    # Try to get SystemSettings if it exists
    try:
        from .models import SystemSettings
        system_settings = SystemSettings.get_active_settings()
        return {
            'dark_mode': request.session.get('dark_mode', False),
            'system_settings': system_settings  # Can be None if no active settings
        }
    except (ImportError, AttributeError, NameError, Exception):
        # Return None if SystemSettings doesn't exist or fails
        return {
            'dark_mode': request.session.get('dark_mode', False),
            'system_settings': None
        }




























