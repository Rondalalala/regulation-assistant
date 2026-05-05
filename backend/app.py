from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import regulations, search

app = FastAPI(title='西北投资制度助理 API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(regulations.router, prefix='/api/regulations')
app.include_router(search.router, prefix='/api/search')

@app.get('/api/health')
def health():
    return {'status': 'ok'}
