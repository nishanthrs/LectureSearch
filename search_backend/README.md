# Web Server: Search Backend

* Implemented via Rust Axum web server framework
* Can be accessed through endpoints:
  * `https://lecturesearch-web.fly.dev/upload?video_url=https://www.youtube.com/watch?v=BAAHVtqKVdQ`
  * `https://lecturesearch-web.fly.dev/search?query=distributed+systems`

## Typesense Rust Client

* No official Rust client supported, so had to use the [Typesense OpenAPI spec](https://github.com/typesense/typesense-rust/blob/main/openapi.yml)
* Generated it via `openapi-generator-cli generate -i typesense_openapi.yml -g rust -o ./typesense_openapi_codegen`
* However, even that codegen cmd didn't work (compiler errors), so I cloned the [Typesense Rust client repo](https://github.com/typesense/typesense-rust/) and moved the `typesense_codegen` pkg to this folder
* Figured out how to write the code by reading [the docs](https://github.com/typesense/typesense-rust/tree/main/typesense_codegen) and the method headers
* Testing it out by starting a local Typesense server: `sudo systemctl start typesense-server.service` (config settings at `/etc/typesense/typesense-server.ini`) and then starting server via `cargo run`

Experiment with other search index offerings ([Meilisearch](https://www.meilisearch.com/docs/reference/api/overview)) or vector DBs ([Qdrant](https://qdrant.tech/documentation/)) for RAG implementation (QA when you click on each video)

## RAG Articles/Sources

* [Building RAG from Scratch](https://docs.llamaindex.ai/en/stable/optimizing/building_rag_from_scratch.html)
* [Langroid Project](https://github.com/langroid/langroid/blob/main/langroid/agent/special/doc_chat_agent.py)
* [LlamaIndex Primer](https://medium.com/@jerryjliu98/how-unstructured-and-llamaindex-can-help-bring-the-power-of-llms-to-your-own-data-3657d063e30d)
* [Difficulties of RAG in Practice and Potential Optimizations](https://news.ycombinator.com/item?id=38643406)
* [Example of BARD Using RAG to Understand Videos](https://news.ycombinator.com/item?id=38406388)
* [Function Calling Thread on r/LocalLlama](https://www.reddit.com/r/LocalLLaMA/comments/16ccszw/do_you_guys_use_function_calling/) (not directly related to RAG, but a useful and powerful technique)
* [OpenAI Cookbook](https://cookbook.openai.com/)
* [Speech Processing and Q&A via Marqo and OpenAI](https://www.marqo.ai/blog/speech-processing) (very similar to this project!)
* [Reliable RAG Systems in MongoDB, LlamaIndex](https://www.patronus.ai/blog/the-10-minute-guide-to-reliable-rag-systems-using-patronus-ai-mongodb-atlas-and-llamaindex)
* [Generating Embeddings](https://simonwillison.net/2023/Oct/23/embeddings/)

## How to Run LLMs

Here are all the options you can use to run LLMs.

### [llama.cpp](https://github.com/ggerganov/llama.cpp)

* Ideal for running on Macs or CPU-based machines
* Download llama.cpp repo
  * `git clone https://github.com/ggerganov/llama.cpp && cd llama.cpp`
* Download the gguf model from HuggingFace
  * Ex. [Mixtral 8x7B MOE repo](https://huggingface.co/TheBloke/Mixtral-8x7B-v0.1-GGUF/tree/main))
* Compile the llama.cpp binary and run with model:
  * `make -j && ./main --color --model ./models/mistral-7b/mistral-7b-instruct-v0.1.Q6_K.gguf -t 7 -b 24 -n -1 --temp 0 -ngl 1 -ins`
  * DISCLAIMER: Runs quite fast on Mac M1! Pretty slow on a CPU server, even a beefy one with 72 cores. Still need to try it out on a GPU with the `--n-gpu-layers` flag

### [Llamafile](https://justine.lol/oneliners/)

Download raw binary of LLM and run it cross-platform

### [vLLMs](https://blog.vllm.ai/2023/06/20/vllm.html)

Pip lib to run models in memory-efficient way

### [Ollama.ai](ollama.ai)

Run as docker containers
