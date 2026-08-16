from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import analysis, edna, insight, region, species, timeline


app = FastAPI(
    title="OceanPulse AI Backend",
    version="0.1.0",
)


# Allow the local frontend development server to call the Backend API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://192.168.1.7:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(analysis.router)
app.include_router(region.router)
app.include_router(insight.router)
app.include_router(timeline.router)
app.include_router(species.router)
app.include_router(edna.router)