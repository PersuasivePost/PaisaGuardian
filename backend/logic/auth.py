"""
JWT Authentication dependency for FastAPI
Verifies tokens with Node.js auth server
"""
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# Node.js auth server configuration
AUTH_SERVER_URL = "http://localhost:3000"
TOKEN_VERIFY_ENDPOINT = f"{AUTH_SERVER_URL}/auth/verify"


class TokenData:
    """Token data extracted from JWT"""
    def __init__(self, user_id: str, email: Optional[str] = None, 
                 roles: Optional[list] = None, **kwargs):
        self.user_id = user_id
        self.email = email
        self.roles = roles or []
        self.extra = kwargs


async def verify_token_with_auth_server(token: str) -> Dict:
    """
    Verify JWT token with Node.js auth server
    
    Args:
        token: JWT token string
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If token is invalid or verification fails
    """
    try:
        logger.info(f"Attempting to verify token with auth server: {TOKEN_VERIFY_ENDPOINT}")
        logger.info(f"Token (first 20 chars): {token[:20]}...")
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                TOKEN_VERIFY_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            
            logger.info(f"Auth server response status: {response.status_code}")
            logger.info(f"Auth server response body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ Token verified for user: {data.get('userId', 'unknown')}")
                return data
            elif response.status_code == 401:
                logger.warning(f"✗ Invalid or expired token. Response: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                logger.error(f"✗ Auth server returned status {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Authentication service unavailable"
                )
                
    except httpx.TimeoutException:
        logger.error("Auth server timeout")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service timeout"
        )
    except httpx.RequestError as e:
        logger.error(f"Auth server connection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot connect to authentication service"
        )
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> TokenData:
    """
    FastAPI dependency to get current authenticated user
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: TokenData = Depends(get_current_user)):
            return {"user_id": user.user_id}
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        TokenData object with user information
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token with Node.js auth server
    user_data = await verify_token_with_auth_server(token)
    
    # Extract user information
    # Adjust field names based on your Node.js server's response format
    user_id = user_data.get("userId") or user_data.get("user_id") or user_data.get("id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return TokenData(
        user_id=str(user_id),
        email=user_data.get("email"),
        roles=user_data.get("roles", []),
        **{k: v for k, v in user_data.items() if k not in ["userId", "user_id", "id", "email", "roles"]}
    )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[TokenData]:
    """
    FastAPI dependency for optional authentication
    Returns None if no token provided, otherwise validates and returns user
    
    Usage:
        @app.get("/public-or-private")
        async def mixed_route(user: Optional[TokenData] = Depends(get_optional_user)):
            if user:
                return {"message": f"Hello {user.user_id}"}
            return {"message": "Hello anonymous"}
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# Health check function for auth service
async def check_auth_service_health() -> bool:
    """
    Check if Node.js auth server is reachable
    
    Returns:
        bool: True if auth service is healthy, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{AUTH_SERVER_URL}/health")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Auth service health check failed: {str(e)}")
        return False
