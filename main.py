from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
config = Config('.env')
oauth = OAuth(config)
app.add_middleware(SessionMiddleware, secret_key="!secret")

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account',  # force to select account
    }
)

# Add CORS middleware
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://accounts.google.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "hello"}


@app.get("/login")
async def login_via_google(request: Request):
    redirect_uri = 'http://localhost:3000/api/auth/callback/google'
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/api/auth/callback/google")
async def auth_via_google(request: Request):
    redirect_uri = 'http://localhost:3000/api/auth/callback/google'
    token = await oauth.google.authorize_access_token(request, redirect_uri=redirect_uri)
    user = await oauth.google.parse_id_token(request, token)
    return dict(user)