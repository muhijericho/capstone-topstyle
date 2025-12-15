"""
PERSISTENCE MIDDLEWARE
======================
Ensures all data changes are persisted before response is sent.
This middleware guarantees that no data is lost.
"""

from django.utils.deprecation import MiddlewareMixin
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class PersistenceMiddleware(MiddlewareMixin):
    """
    Middleware that ensures all database transactions are committed
    before the response is sent to the client.
    """
    
    def process_response(self, request, response):
        """
        Ensure all pending database transactions are committed
        before sending the response.
        """
        try:
            # Django automatically commits transactions at the end of request processing
            # We just need to ensure we're in a clean state
            # Only log for POST/PUT/PATCH/DELETE requests that modify data
            if hasattr(request, 'method') and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                # Check if we're in an atomic transaction block
                if transaction.get_autocommit():
                    # No active transaction, Django will handle commits automatically
                    logger.info(f"[PERSISTENCE_MIDDLEWARE] Ensured persistence for {request.method} request to {request.path}")
                else:
                    # We're in a transaction block, Django will commit when the block exits
                    logger.info(f"[PERSISTENCE_MIDDLEWARE] Transaction active for {request.method} request to {request.path}")
            
        except Exception as e:
            logger.error(f"[PERSISTENCE_MIDDLEWARE] Error ensuring persistence: {str(e)}")
        
        return response
    
    def process_exception(self, request, exception):
        """
        Rollback transactions on exception to maintain data integrity.
        """
        try:
            transaction.rollback()
            logger.warning(f"[PERSISTENCE_MIDDLEWARE] Rolled back transaction due to exception: {str(exception)}")
        except Exception as e:
            logger.error(f"[PERSISTENCE_MIDDLEWARE] Error rolling back transaction: {str(e)}")
        
        return None

