from fastapi import FastAPI

from .routes import analysis, edna, insight, region, species, timeline
app = FastAPI(
    title="OceanPulse AI Backend",
    version="0.1.0",
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