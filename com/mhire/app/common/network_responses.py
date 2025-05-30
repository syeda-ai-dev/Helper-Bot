from typing import Dict, Any, Optional
from fastapi.responses import JSONResponse
from com.mhire.app.common.exceptions import BaseError

class NetworkResponse:
    """Handles standardized network responses across the application"""
    
    @staticmethod
    def success_response(
        http_code: int = 200,
        message: str = "Success",
        data: Optional[Dict[str, Any]] = None,
        resource: str = "",
        duration: float = 0.0
    ) -> JSONResponse:
        """Creates a standardized success response"""
        return JSONResponse(
            status_code=http_code,
            content={
                "success": True,
                "message": message,
                "data": data or {},
                "resource": resource,
                "duration": f"{duration:.3f}s"
            }
        )
    
    @staticmethod
    def error_response(
        error: BaseError,
        resource: str = "",
        duration: float = 0.0
    ) -> JSONResponse:
        """Creates a standardized error response"""
        return JSONResponse(
            status_code=error.http_status_code,
            content={
                "success": False,
                "error": {
                    "code": error.error_code,
                    "message": error.message
                },
                "resource": resource,
                "duration": f"{duration:.3f}s"
            }
        )