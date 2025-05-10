# ---- Builder ----
FROM python:3.12.4-alpine AS build

RUN pip install fastapi uvicorn httpx[cli,http2]
RUN pip install sqlalchemy psycopg2-binary pymysql asyncpg aiomysql
RUN pip install redis aio_pika python-jose pycryptodome colorama
RUN pip install openai agno
RUN pip install annotated-types anyio certifi click distro h11 httpcore idna jiter
RUN pip install pydantic pydantic_core python-dotenv sniffio starlette tqdm typing_extensions
RUN pip install backoff seleniumbase goplus

FROM build AS deploy

WORKDIR /app

COPY . .