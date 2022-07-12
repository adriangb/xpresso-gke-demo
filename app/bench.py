import logging
import re
from asyncio import subprocess
from typing import Annotated

import anyio
import uvicorn  # type: ignore
from pydantic import BaseModel, BaseSettings, Field
from xpresso import App, FromQuery, Path

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AppConfig(BaseSettings):
    gunicorn_host: str
    uvicorn_host: str


class BenchmarkParams(BaseModel):
    connections: int = 1024
    threads: int = 32
    duration: int = 30


async def bench(endpoint: str, params: BenchmarkParams) -> float:
    options = f"-c {params.connections} -t {params.threads} -d {params.duration}"
    cmd = f"go-wrk {options} {endpoint}"
    logger.info(f"Running '{cmd}'")
    res = await anyio.run_process(cmd, stdout=subprocess.PIPE)
    # check for errors
    assert res.returncode == 0
    match = re.search(r"20X [rR]esponses:\s*[0-9]+\s*\((\d+(?:\.\d+)?)%\)", res.stdout.decode())
    assert match is not None, res.stdout.decode()
    assert float(match.group(1)) == 100
    # parse result
    match = re.search(r"Requests per second:\s+([0-9]+\.[0-9]+)", res.stdout.decode())
    assert match is not None, res.stdout.decode()
    return float(match.group(1))


RequestRate = Annotated[float, Field(description="req/s")]


class BenchmarkResult(BaseModel):
    gunicorn: RequestRate
    uvicorn: RequestRate


class RunResults(BaseModel):
    primes: BenchmarkResult
    images: BenchmarkResult


async def run_wrk(params: FromQuery[BenchmarkParams]) -> RunResults:
    """Run go-wrk (https://github.com/adjust/go-wrk) against the APIs"""
    cfg = AppConfig()  # type: ignore
    return RunResults(
        primes=BenchmarkResult(
            gunicorn=await bench(f"{cfg.gunicorn_host}/primes?n=100", params),
            uvicorn=await bench(f"{cfg.uvicorn_host}/primes?n=100", params),
        ),
        images=BenchmarkResult(
            gunicorn=await bench(f"{cfg.gunicorn_host}/image", params),
            uvicorn=await bench(f"{cfg.uvicorn_host}/image", params),
        ),
    )


app = App(
    routes=[
        Path("/load", post=run_wrk),
    ],
)


async def main() -> None:
    cfg = uvicorn.Config(app, host="0.0.0.0", port=80, access_log=False)
    server = uvicorn.Server(cfg)
    await server.serve()


if __name__ == "__main__":
    anyio.run(main)
