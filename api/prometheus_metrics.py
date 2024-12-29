from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from fastapi import FastAPI, Request

class PrometheusMetrics:
    def __init__(self):
        # Initialize the error counter
        self.error_counter = Counter(
            "api_errors_total", "Total errors per endpoint", ["endpoint", "method", "status"]
        )

    def register_metrics(self, instrumentator: Instrumentator) -> Instrumentator:
        """
        Registers custom metrics to the Instrumentator.
        """
        # Collect average response times per endpoint
        instrumentator.add(
            lambda: metrics.latency(
                metric_name="http_request_duration_seconds",
                labels={"handler": lambda request: request.scope.get("path", "unknown")},
            )
        )
        # Error counter
        instrumentator.add(
            lambda: metrics.default(
                metric_name="http_errors_total",
                documentation="Total HTTP errors",
                labels={"handler": lambda request: request.scope.get("path", "unknown")},
            )
        )
        return instrumentator

    def setup(self, app: FastAPI):
        """
        Configures the Instrumentator with custom metrics, exposes it to the app,
        and adds the error counting middleware.
        """
        # Register and expose metrics
        instrumentator = Instrumentator()
        self.register_metrics(instrumentator).instrument(app).expose(app)

        # Add middleware for error counting
        @app.middleware("http")
        async def count_errors_middleware(request: Request, call_next):
            try:
                response = await call_next(request)
                if response.status_code >= 400:
                    self.error_counter.labels(
                        endpoint=request.url.path, method=request.method, status=response.status_code
                    ).inc()
                return response
            except Exception as e:
                self.error_counter.labels(
                    endpoint=request.url.path, method=request.method, status=500
                ).inc()
                raise e
