from fastapi.security import OAuth2PasswordBearer

oauth2_scheme= OAuth2PasswordBearer(tokenUrl="/api/vi/auth/login")  # Le decimos a Fastapi ue los toquen se obtendran de esta url 
