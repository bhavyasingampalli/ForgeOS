from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.identity import User
from app.models.connection import WorkspaceConnection, Credential
from app.utils.config import settings
from app.utils.crypto import crypto_service
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

router = APIRouter(prefix="/api/oauth", tags=["oauth"])

config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='github',
    client_id=settings.GITHUB_CLIENT_ID if hasattr(settings, 'GITHUB_CLIENT_ID') else "mock_id",
    client_secret=settings.GITHUB_CLIENT_SECRET if hasattr(settings, 'GITHUB_CLIENT_SECRET') else "mock_secret",
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    client_kwargs={'scope': 'repo user'}
)

from app.models.identity import User, Session as AuthSession
import datetime

@router.get("/{provider}/login")
async def oauth_login(provider: str, request: Request, db: Session = Depends(get_db)):
    session_val = request.cookies.get("forgeos_session")
    if not session_val:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    auth_session = db.query(AuthSession).filter(
        AuthSession.token == session_val,
        AuthSession.expires_at > datetime.datetime.utcnow()
    ).first()
    
    if not auth_session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
        
    user_id = auth_session.user_id

    # Store user_id in Starlette session so we know who is connecting after callback
    request.session['oauth_user_id'] = user_id
    
    if provider == 'github':
        redirect_uri = request.url_for('oauth_callback', provider=provider)
        return await oauth.github.authorize_redirect(request, str(redirect_uri))
    elif provider in ['google', 'notion', 'gmail', 'google_drive', 'google_calendar']:
        # For hackathon/demo purposes, immediately redirect to the callback for non-GitHub providers
        redirect_uri = request.url_for('oauth_callback', provider=provider)
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=str(redirect_uri), status_code=302)
    
    raise HTTPException(status_code=400, detail="Provider not supported")

@router.get("/{provider}/callback")
async def oauth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get('oauth_user_id')
    if not user_id:
        raise HTTPException(status_code=400, detail="User session not found")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if provider in ['github', 'google', 'notion', 'gmail', 'google_drive', 'google_calendar']:
        if provider == 'github':
            token = await oauth.github.authorize_access_token(request)
            if not token:
                raise HTTPException(status_code=401, detail="Failed to retrieve GitHub access token")
            access_token = token.get('access_token')
            scope = token.get('scope', 'repo user')
        else:
            access_token = f"mock_{provider}_access_token_for_demo"
            scope = "all"
            
        encrypted_token = crypto_service.encrypt_token(access_token)
            
        # Title case for DB consistency (e.g. 'Slack', 'Google')
        provider_display = provider.title()
            
        # Update or create WorkspaceConnection
        conn = db.query(WorkspaceConnection).filter(
            WorkspaceConnection.user_id == user.id,
            WorkspaceConnection.provider == provider_display
        ).first()
        
        if not conn:
            conn = WorkspaceConnection(
                user_id=user.id,
                provider=provider_display,
                status='CONNECTED'
            )
            db.add(conn)
            db.commit()
            db.refresh(conn)
            
            cred = Credential(
                connection_id=conn.id,
                encrypted_access_token=encrypted_token,
                scope=scope
            )
            db.add(cred)
        else:
            conn.status = 'CONNECTED'
            if not conn.credential:
                cred = Credential(connection_id=conn.id, encrypted_access_token=encrypted_token, scope=scope)
                db.add(cred)
            else:
                conn.credential.encrypted_access_token = encrypted_token
                conn.credential.scope = scope
            
        db.commit()
        
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="http://localhost:5173/integrations", status_code=302)
    
    raise HTTPException(status_code=400, detail="Callback failed")
