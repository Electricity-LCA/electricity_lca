A calculation microservice built using FastAPI that performs calculations and returns the response using Feather

Some principles:
* Use feather format - This allows serializing DataFrames efficiently into a binary format that retains types and schemas. Much faster than JSON.
* Chunk responses - If sending large DataFrames, use pagination or chunking to send parts of the DF at a time instead of the whole thing.
* Column selection - Allow the frontend to specify columns to return rather than the whole DF to minimize data transfer.
* Data compression - Compress the serialized DataFrame using gzip/zlib before sending over the network.
* Caching - Implement caching layers to avoid re-fetching the same data.
* Streaming - Stream the DataFrame back incrementally rather than all at once if possible.
* Use DB backend - Store DataFrames in a database/data warehouse and query from frontend vs. passing directly.
* Async processing - Use message queue with Celery/Redis to asynchronously process and deliver DataFrames.
* Type hints - Use type hints and schemas to ensure correct DataFrame structure.
* HTTP compression - Enable gzip compression on the HTTP API response for smaller payloads.
