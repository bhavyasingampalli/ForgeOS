import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.identity import User, OAuthAccount, Session as AuthSession
from app.models.connection import WorkspaceConnection, Credential
from app.utils.config import settings
from app.utils.crypto import crypto_service
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

router = APIRouter(prefix="/api/auth", tags=["auth"])

config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID if hasattr(settings, 'GOOGLE_CLIENT_ID') else "mock_id",
    client_secret=settings.GOOGLE_CLIENT_SECRET if hasattr(settings, 'GOOGLE_CLIENT_SECRET') else "mock_secret",
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/drive.readonly'
    }
)

@router.get("/signin")
async def signin(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, str(redirect_uri))

@router.get("/callback")
async def auth_callback(request: Request, response: Response, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        access_token = token.get('access_token')
    except Exception:
        # Fallback for hackathon demo if actual OAuth fails
        user_info = {"email": "demo@forgeos.ai", "name": "Demo User", "sub": "12345"}
        access_token = "mock_google_token"
        
    email = user_info.get('email')
    name = user_info.get('name')
    provider_user_id = user_info.get('sub')
    
    # 1. ForgeOS User Identity Created
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
        
    # 2. ForgeOS OAuth Account Linking
    oauth_acc = db.query(OAuthAccount).filter(OAuthAccount.provider_user_id == provider_user_id, OAuthAccount.provider == 'Google').first()
    if not oauth_acc:
        oauth_acc = OAuthAccount(user_id=user.id, provider='Google', provider_user_id=provider_user_id)
        db.add(oauth_acc)
        db.commit()
        
    # Auto-disconnect other platforms on fresh login for demo purposes
    conns_to_remove = db.query(WorkspaceConnection).filter(
        WorkspaceConnection.user_id == user.id, 
        WorkspaceConnection.provider != 'Google'
    ).all()
    for c in conns_to_remove:
        db.query(Credential).filter(Credential.connection_id == c.id).delete()
        db.delete(c)
    db.commit()
        
    # 3. Google Workspace Connection & Encrypted Credential
    conn = db.query(WorkspaceConnection).filter(
        WorkspaceConnection.user_id == user.id,
        WorkspaceConnection.provider == 'Google'
    ).first()
    
    encrypted_token = crypto_service.encrypt_token(access_token)
    
    if not conn:
        conn = WorkspaceConnection(
            user_id=user.id,
            provider='Google',
            status='CONNECTED'
        )
        db.add(conn)
        db.commit()
        db.refresh(conn)
        
        cred = Credential(
            connection_id=conn.id,
            encrypted_access_token=encrypted_token,
            scope="openid email profile calendar drive"
        )
        db.add(cred)
    else:
        conn.status = 'CONNECTED'
        if not conn.credential:
            cred = Credential(connection_id=conn.id, encrypted_access_token=encrypted_token)
            db.add(cred)
        else:
            conn.credential.encrypted_access_token = encrypted_token
            
    db.commit()

    # 4. Create Session (Set HttpOnly Cookie)
    session_token = str(uuid.uuid4())
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    
    auth_session = AuthSession(user_id=user.id, token=session_token, expires_at=expires_at)
    db.add(auth_session)
    db.commit()
    
    redirect_response = RedirectResponse(url="http://localhost:5173/integrations", status_code=302)
    redirect_response.set_cookie(
        key="forgeos_session",
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=86400
    )
    
    return redirect_response

@router.get("/me")
async def get_me(request: Request, db: Session = Depends(get_db)):
    # Authenticate via HttpOnly cookie
    session_val = request.cookies.get("forgeos_session")
    if not session_val:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    auth_session = db.query(AuthSession).filter(
        AuthSession.token == session_val,
        AuthSession.expires_at > datetime.datetime.utcnow()
    ).first()
    
    if not auth_session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
        
    user = db.query(User).filter(User.id == auth_session.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    connections = db.query(WorkspaceConnection).filter(WorkspaceConnection.user_id == user.id).all()
    return {
        "user_id": user.id,
        "email": user.email,
        "name": user.name,
        "connections": [{"provider": c.provider, "status": c.status} for c in connections]
    }

@router.post("/logout")
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    session_val = request.cookies.get("forgeos_session")
    if session_val:
        auth_session = db.query(AuthSession).filter(AuthSession.token == session_val).first()
        if auth_session:
            # Clear connections for a clean demo slate
            conns_to_remove = db.query(WorkspaceConnection).filter(WorkspaceConnection.user_id == auth_session.user_id).all()
            for c in conns_to_remove:
                db.query(Credential).filter(Credential.connection_id == c.id).delete()
                db.delete(c)
            db.delete(auth_session)
            db.commit()
    
    res = Response(status_code=200)
    res.delete_cookie("forgeos_session")
    return res
