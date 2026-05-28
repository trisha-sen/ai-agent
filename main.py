import os
from contextlib import asynccontextmanager

import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, Query

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://localhost/research_db")

pool: asyncpg.Pool | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)
    yield
    await pool.close()


app = FastAPI(title="Abstract Search", lifespan=lifespan)


@app.get("/health")
async def health():
    count = await pool.fetchval("SELECT COUNT(*) FROM papers")
    return {"status": "ok", "rows_loaded": count}


@app.get("/search")
async def search(
    q: str = Query(..., min_length=1, description="Case-insensitive substring"),
    year: int | None = Query(None, description="Filter by exact year"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    conditions = ["(title ILIKE $1 OR abstract ILIKE $1)"]
    args: list = [f"%{q}%"]

    if year is not None:
        conditions.append(f"year = ${len(args) + 1}")
        args.append(year)

    where = " AND ".join(conditions)
    total = await pool.fetchval(f"SELECT COUNT(*) FROM papers WHERE {where}", *args)

    rows = await pool.fetch(
        f"""
        SELECT doi, title, authors, author_keywords, journal, year, cited_by
        FROM papers
        WHERE {where}
        ORDER BY cited_by DESC NULLS LAST, year DESC
        LIMIT ${len(args) + 1} OFFSET ${len(args) + 2}
        """,
        *args, limit, offset,
    )

    return {
        "query": q,
        "year": year,
        "total": total,
        "returned": len(rows),
        "results": [
            {
                "title": r["title"],
                "authors": r["authors"],
                "year": r["year"],
                "cited_by": r["cited_by"],
                "journal": r["journal"],
                "doi": r["doi"],
                "author_keywords": r["author_keywords"],
            }
            for r in rows
        ],
    }
