from django.core.management.commands.runserver import Command as RunserverCommand
from django.core.management.base import CommandError
import sys
import os

class Command(RunserverCommand):
    help = 'Starts a development server without the production warning'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store original stdout and stderr
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        # Create filtered output handlers
        self._filtered_stdout = self._create_filtered_stream(sys.stdout)
        self._filtered_stderr = self._create_filtered_stream(sys.stderr)
    
    def check(self, *args, **options):
        """Override check to suppress development server warnings"""
        # Temporarily replace stderr to filter warnings
        original_stderr = sys.stderr
        sys.stderr = self._filtered_stderr
        
        try:
            # Call parent check (this is where the warning is printed)
            return super().check(*args, **options)
        finally:
            # Restore stderr
            sys.stderr = original_stderr
    
    def _create_filtered_stream(self, original_stream):
        """Create a filtered stream that suppresses development server warnings"""
        class FilteredStream:
            def __init__(self, original):
                self.original = original
                self._buffer = []
                self._skip_next_lines = 0
                
            def write(self, text):
                if not text:
                    return
                
                # Convert bytes to string if needed
                if isinstance(text, bytes):
                    try:
                        text = text.decode('utf-8')
                    except:
                        self.original.write(text)
                        return
                
                # Check for warning patterns
                text_lower = text.lower()
                if any(keyword in text_lower for keyword in [
                    'warning: this is a development server',
                    'do not use it in a production setting',
                    'use a production wsgi or asgi server instead',
                    'for more information on production servers'
                ]):
                    # Skip this line and potentially the next line (URL line)
                    return
                
                # Check if this is part of a multi-line warning
                if 'warning' in text_lower and 'development' in text_lower:
                    return
                
                # Write to original stream
                self.original.write(text)
                
            def flush(self):
                self.original.flush()
                
            def __getattr__(self, name):
                # Delegate all other attributes to original stream
                return getattr(self.original, name)
        
        return FilteredStream(original_stream)
    
    def handle(self, *args, **options):
        """Override handle to set up filtered streams before running"""
        # Set filtered streams
        sys.stdout = self._filtered_stdout
        sys.stderr = self._filtered_stderr
        
        try:
            # Call parent handle
            return super().handle(*args, **options)
        finally:
            # Restore original streams
            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr
    
    def inner_run(self, *args, **options):
        """Override inner_run to ensure streams are filtered during server startup"""
        # Ensure streams are filtered
        sys.stdout = self._filtered_stdout
        sys.stderr = self._filtered_stderr
        
        try:
            # Call parent inner_run
            return super().inner_run(*args, **options)
        finally:
            # Don't restore here - let handle() do it
            pass




































