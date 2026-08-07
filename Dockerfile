FROM python:3.12-slim

WORKDIR /app
COPY vendor/deliveryguard-0.2.0-py3-none-any.whl /tmp/deliveryguard-0.2.0-py3-none-any.whl
RUN pip install --no-cache-dir /tmp/deliveryguard-0.2.0-py3-none-any.whl
COPY . .
RUN pip install --no-cache-dir .

ENTRYPOINT ["adapterproof"]
CMD ["run", "--database-dir", "/tmp/adapterproof"]
