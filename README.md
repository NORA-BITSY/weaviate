<h1>Weaviate <img alt='Weaviate logo' src='https://weaviate.io/img/site/weaviate-logo-light.png' width='148' align='right' /></h1>

[![Go Reference](https://pkg.go.dev/badge/github.com/weaviate/weaviate.svg)](https://pkg.go.dev/github.com/weaviate/weaviate)
[![Build Status](https://github.com/weaviate/weaviate/actions/workflows/.github/workflows/pull_requests.yaml/badge.svg?branch=main)](https://github.com/weaviate/weaviate/actions/workflows/.github/workflows/pull_requests.yaml)
[![Go Report Card](https://goreportcard.com/badge/github.com/weaviate/weaviate)](https://goreportcard.com/report/github.com/weaviate/weaviate)
[![Coverage Status](https://codecov.io/gh/weaviate/weaviate/branch/main/graph/badge.svg)](https://codecov.io/gh/weaviate/weaviate)
[![Slack](https://img.shields.io/badge/slack--channel-blue?logo=slack)](https://weaviate.io/slack)
[![GitHub Tutorials](https://img.shields.io/badge/Weaviate_Tutorials-green)](https://github.com/weaviate-tutorials/)

## Overview

Weaviate is a cloud-native, **open source vector database** that is robust, fast, and scalable.

To get started quickly, have a look at one of these pages:

- [Quickstart tutorial](https://weaviate.io/developers/weaviate/quickstart) To see Weaviate in action
- [Installation & Setup Guide](#installation--setup) Below for detailed setup instructions
- [Contributor guide](https://weaviate.io/developers/contributor-guide) To contribute to this project

For more details, read through the summary on this page or see the system [documentation](https://weaviate.io/developers/weaviate/).

---

## Why Weaviate?

Weaviate uses state-of-the-art machine learning (ML) models to turn your data - text, images, and more - into a searchable vector database.

Here are some highlights.

### Speed

Weaviate is fast. The core engine can run a 10-NN nearest neighbor search on millions of objects in milliseconds. See [benchmarks](https://weaviate.io/developers/weaviate/benchmarks).

### Flexibility

Weaviate can **vectorize your data at import time**. Or, if you have already vectorized your data, you can **upload your own vectors** instead.

Modules give you the flexibility to tune Weaviate for your needs. More than two dozen modules connect you to popular services and model hubs such as [OpenAI](https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules/text2vec-openai), [Cohere](https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules/text2vec-cohere), [VoyageAI](https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules/text2vec-voyageai) and [HuggingFace](https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules/text2vec-huggingface). Use custom modules to work with your own models or third party services.

### Production-readiness

Weaviate is built with [scaling](https://weaviate.io/developers/weaviate/concepts/cluster), [replication](https://weaviate.io/developers/weaviate/concepts/replication-architecture), and [security](https://weaviate.io/developers/weaviate/configuration/authentication) in mind so you can go smoothly from **rapid prototyping** to **production at scale**.

### Beyond search

Weaviate doesn't just power lightning-fast vector searches. Other superpowers include **recommendation**, **summarization**, and **integration with neural search frameworks**.

## Who uses Weaviate?

- **Software Engineers**

  - Weaviate is an ML-first database engine
  - Out-of-the-box modules for AI-powered searches, automatic classification, and LLM integration
   - Full CRUD support
   - Cloud-native, distributed system that runs well on Kubernetes
   - Scales with your workloads

- **Data Engineers**

  - Weaviate is a fast, flexible vector database
  - Use your own ML model or third party models
  - Run locally or with an inference service

- **Data Scientists**

   - Seamless handover of Machine Learning models to engineers and MLOps
   - Deploy and maintain your ML models in production reliably and efficiently
   - Easily package custom trained models

## What can you build with Weaviate?

A Weaviate vector database can search text, images, or a combination of both. Fast vector search provides a foundation for chatbots, recommendation systems, summarizers, and classification systems.

Here are some examples that show how Weaviate integrates with other AI and ML tools:

### Use Weaviate with third party embeddings

- [Cohere](https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules/text2vec-cohere) ([blogpost](https://txt.cohere.com/embedding-archives-wikipedia/))
- [Hugging Face](https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules/text2vec-huggingface)
- [OpenAI](https://github.com/openai/openai-cookbook/tree/main/examples/vector_databases/weaviate)

### Use Weaviate as a document store

- [DocArray](https://docarray.jina.ai/advanced/document-store/weaviate/)
- [Haystack](https://docs.haystack.deepset.ai/reference/integrations-weaviate#weaviatedocumentstore) ([blogpost](https://www.deepset.ai/weaviate-vector-search-engine-integration))

### Use Weaviate as a memory backend

- [Auto-GPT](https://github.com/Significant-Gravitas/Auto-GPT/blob/master/docs/configuration/memory.md#weaviate-setup) ([blogpost](https://weaviate.io/blog/autogpt-and-weaviate))
- [LangChain](https://python.langchain.com/docs/integrations/providers/weaviate) ([blogpost](https://weaviate.io/blog/combining-langchain-and-weaviate))
- [LlamaIndex](https://gpt-index.readthedocs.io/en/latest/how_to/integrations/vector_stores.html) ([blogpost](https://weaviate.io/blog/llamaindex-and-weaviate))
- [OpenAI - ChatGPT retrieval plugin](https://github.com/openai/chatgpt-retrieval-plugin/blob/main/docs/providers/weaviate/setup.md)

### Demos

These demos are working applications that highlight some of Weaviate's capabilities. Their source code is available on GitHub.

- [Verba, the Golden RAGtreiver](https://verba.weaviate.io) ([GitHub](https://github.com/weaviate/verba))
- [Healthsearch](https://healthsearch.weaviate.io) ([GitHub](https://github.com/weaviate/healthsearch-demo))
- [Awesome-Moviate](https://awesome-moviate.weaviate.io/) ([GitHub](https://github.com/weaviate-tutorials/awesome-moviate))

## How can you connect to Weaviate?

Weaviate exposes a [GraphQL API](https://weaviate.io/developers/weaviate/api/graphql) and a [REST API](https://weaviate.io/developers/weaviate/api/rest). Starting in v1.23, a new [gRPC API](https://weaviate.io/developers/weaviate/api/grpc) provides even faster access to your data.

Weaviate provides client libraries for several popular languages:

- [Python](https://weaviate.io/developers/weaviate/client-libraries/python)
- [JavaScript/TypeScript](https://weaviate.io/developers/weaviate/client-libraries/typescript)
- [Go](https://weaviate.io/developers/weaviate/client-libraries/go)
- [Java](https://weaviate.io/developers/weaviate/client-libraries/java)

There are also [community supported libraries](https://weaviate.io/developers/weaviate/client-libraries/community) for additional languages.

## Where can You learn more?

Free, self-paced courses in [Weaviate Academy](https://weaviate.io/developers/academy) teach you how to use Weaviate. The [Tutorials repo](https://github.com/weaviate-tutorials) has code for example projects. The [Recipes repo](https://github.com/weaviate/recipes) has even more project code to get you started.

The [Weaviate blog](https://weaviate.io/blog) and [podcast](https://weaviate.io/podcast) regularly post stories on Weaviate and AI.

Here are some popular posts:

### Blogs

- [What to expect from Weaviate in 2023](https://weaviate.io/blog/what-to-expect-from-weaviate-in-2023)
- [Why is vector search so fast?](https://weaviate.io/blog/Why-is-Vector-Search-so-fast)
- [Cohere Multilingual ML Models with Weaviate](https://weaviate.io/blog/Cohere-multilingual-with-weaviate)
- [Vamana vs. HNSW - Exploring ANN algorithms Part 1](https://weaviate.io/blog/ann-algorithms-vamana-vs-hnsw)
- [HNSW+PQ - Exploring ANN algorithms Part 2.1](https://weaviate.io/blog/ann-algorithms-hnsw-pq)
- [The Tile Encoder - Exploring ANN algorithms Part 2.2](https://weaviate.io/blog/ann-algorithms-tiles-enocoder)
- [How GPT4.0 and other Large Language Models Work](https://weaviate.io/blog/what-are-llms)
- [Monitoring Weaviate in Production](https://weaviate.io/blog/monitoring-weaviate-in-production)
- [The ChatGPT Retrieval Plugin - Weaviate as a Long-term Memory Store for Generative AI](https://weaviate.io/blog/weaviate-retrieval-plugin)
- [Combining LangChain and Weaviate](https://weaviate.io/blog/combining-langchain-and-weaviate)
- [How to build an Image Search Application with Weaviate](https://weaviate.io/blog/how-to-build-an-image-search-application-with-weaviate)
- [Building Multimodal AI in TypeScript](https://weaviate.io/blog/multimodal-search-in-typescript)
- [Giving Auto-GPT Long-Term Memory with Weaviate](https://weaviate.io/blog/autogpt-and-weaviate)

### Podcasts

- [Neural Magic in Weaviate](https://www.youtube.com/watch?v=leGgjIQkVYo)
- [BERTopic](https://www.youtube.com/watch?v=IwXOaHanfUU)
- [Jina AI's Neural Search Framework](https://www.youtube.com/watch?v=o6MD0tWl0SM)

### Other reading

- [Weaviate is an open-source search engine powered by ML, vectors, graphs, and GraphQL (ZDNet)](https://www.zdnet.com/article/weaviate-an-open-source-search-engine-powered-by-machine-learning-vectors-graphs-and-graphql/)
- [Weaviate, an ANN Database with CRUD support (DB-Engines.com)](https://db-engines.com/en/blog_post/87)
- [A sub-50ms neural search with DistilBERT and Weaviate (Towards Datascience)](https://towardsdatascience.com/a-sub-50ms-neural-search-with-distilbert-and-weaviate-4857ae390154)
- [Getting Started with Weaviate Python Library (Towards Datascience)](https://towardsdatascience.com/getting-started-with-weaviate-python-client-e85d14f19e4f)

## Join our community!

At Weaviate, we love to connect with our community. We love helping amazing people build cool things. And, we love to talk with you about you passion for vector databases and AI.

Please reach out, and join our community:

- [Community forum](https://forum.weaviate.io)
- [GitHub](https://github.com/weaviate/weaviate)
- [Slack](https://weaviate.io/slack)
- [X (Twitter)](https://twitter.com/weaviate_io)

To keep up to date with new releases, meetup news, and more, subscribe to our [newsletter](https://newsletter.weaviate.io/)

---

# Installation & Setup

This guide provides comprehensive instructions for installing and running Weaviate in various environments.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Start with Docker Compose](#quick-start-with-docker-compose)
3. [Production Docker Setup](#production-docker-setup)
4. [Development Setup](#development-setup)
5. [Cluster Setup](#cluster-setup)
6. [Module Configuration](#module-configuration)
7. [Environment Variables](#environment-variables)
8. [Building from Source](#building-from-source)
9. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

- **Operating System**: Linux, macOS, or Windows with Docker support
- **Memory**: 4GB RAM minimum, 8GB+ recommended for production
- **Storage**: 10GB available disk space minimum
- **Docker**: Version 20.10+ with Docker Compose v2.0+
- **Go**: Version 1.22+ (for building from source)

### Recommended Production Requirements

- **Memory**: 16GB+ RAM
- **CPU**: 4+ cores
- **Storage**: SSD with 100GB+ available space
- **Network**: Stable internet connection for module downloads

## Quick Start with Docker Compose

The fastest way to get Weaviate running is with Docker Compose.

### 1. Generate Configuration

Visit the [Weaviate Configuration Tool](https://weaviate.io/developers/weaviate/installation/docker-compose) to generate a custom `docker-compose.yml` file with your desired modules and settings.

### 2. Basic Setup

Create a basic `docker-compose.yml` file:

```yaml
version: '3.4'
services:
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
      - "50051:50051"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'none'
      ENABLE_MODULES: ''
      CLUSTER_HOSTNAME: 'node1'
    volumes:
      - weaviate_data:/var/lib/weaviate
volumes:
  weaviate_data:
```

### 3. Start Weaviate

```bash
docker compose up -d
```

### 4. Verify Installation

Check if Weaviate is running:

```bash
curl http://localhost:8080/v1/.well-known/ready
```

You should see a `200 OK` response.

## Production Docker Setup

For production environments, consider these additional configurations:

### 1. Resource Limits

```yaml
services:
  weaviate:
    image: semitechnologies/weaviate:latest
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'
        reservations:
          memory: 4G
          cpus: '2'
    # ... other configuration
```

### 2. Health Checks

```yaml
services:
  weaviate:
    # ... other configuration
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/v1/.well-known/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

### 3. Logging Configuration

```yaml
services:
  weaviate:
    # ... other configuration
    environment:
      LOG_LEVEL: 'info'
      LOG_FORMAT: 'json'
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"
```

### 4. Backup Configuration

For S3 backup support:

```yaml
services:
  weaviate:
    # ... other configuration
    environment:
      ENABLE_MODULES: 'backup-s3'
      BACKUP_S3_BUCKET: 'my-weaviate-backups'
      AWS_ACCESS_KEY_ID: 'your-access-key'
      AWS_SECRET_ACCESS_KEY: 'your-secret-key'
      AWS_REGION: 'us-east-1'
```

## Development Setup

For development and testing purposes:

### 1. Clone the Repository

```bash
git clone https://github.com/weaviate/weaviate.git
cd weaviate
```

### 2. Development Environment with Docker

Use the provided development scripts:

```bash
# Start development environment
./tools/dev/restart_dev_environment.sh

# Start Weaviate development server
./tools/dev/run_dev_server.sh
```

### 3. Available Development Options

The development environment supports various modules:

```bash
# With text transformers
./tools/dev/restart_dev_environment.sh --transformers

# With contextionary
./tools/dev/restart_dev_environment.sh --contextionary

# With multiple modules
./tools/dev/restart_dev_environment.sh --transformers --qna --sum

# With backup modules
./tools/dev/restart_dev_environment.sh --s3
./tools/dev/restart_dev_environment.sh --gcs
./tools/dev/restart_dev_environment.sh --azure

# With monitoring
./tools/dev/restart_dev_environment.sh --prometheus
```

### 4. Debug Setup

For debugging with Delve:

```bash
./tools/dev/run_debug_server.sh
```

## Cluster Setup

### 1. Three-Node Cluster with Raft

Generate a cluster configuration:

```bash
cd docker-compose-raft
./raft_cluster.sh 3  # Creates a 3-node cluster
```

Start the cluster:

```bash
docker-compose -f docker-compose-raft.yml up -d
```

### 2. Manual Cluster Configuration

For a manual cluster setup:

```yaml
version: '3.4'
services:
  weaviate-node-1:
    image: semitechnologies/weaviate:latest
    environment:
      CLUSTER_HOSTNAME: 'node1'
      CLUSTER_GOSSIP_BIND_PORT: '7100'
      CLUSTER_DATA_BIND_PORT: '7101'
      RAFT_PORT: '8300'
      RAFT_INTERNAL_RPC_PORT: '8301'
      RAFT_JOIN: 'node1,node2,node3'
      RAFT_BOOTSTRAP_EXPECT: '3'
    ports:
      - "8080:8080"
      - "7100:7100"
      - "7101:7101"
      - "8300:8300"

  weaviate-node-2:
    image: semitechnologies/weaviate:latest
    environment:
      CLUSTER_HOSTNAME: 'node2'
      CLUSTER_GOSSIP_BIND_PORT: '7102'
      CLUSTER_DATA_BIND_PORT: '7103'
      CLUSTER_JOIN: 'node1:7100'
      RAFT_PORT: '8302'
      RAFT_INTERNAL_RPC_PORT: '8303'
      RAFT_JOIN: 'node1,node2,node3'
      RAFT_BOOTSTRAP_EXPECT: '3'
    ports:
      - "8081:8080"
      - "7102:7102"
      - "7103:7103"
      - "8302:8302"

  weaviate-node-3:
    image: semitechnologies/weaviate:latest
    environment:
      CLUSTER_HOSTNAME: 'node3'
      CLUSTER_GOSSIP_BIND_PORT: '7104'
      CLUSTER_DATA_BIND_PORT: '7105'
      CLUSTER_JOIN: 'node1:7100'
      RAFT_PORT: '8304'
      RAFT_INTERNAL_RPC_PORT: '8305'
      RAFT_JOIN: 'node1,node2,node3'
      RAFT_BOOTSTRAP_EXPECT: '3'
    ports:
      - "8082:8080"
      - "7104:7104"
      - "7105:7105"
      - "8304:8304"
```

## Module Configuration

### 1. Text Vectorizers

#### OpenAI
```yaml
environment:
  ENABLE_MODULES: 'text2vec-openai'
  OPENAI_APIKEY: 'your-openai-api-key'
  DEFAULT_VECTORIZER_MODULE: 'text2vec-openai'
```

#### Cohere
```yaml
environment:
  ENABLE_MODULES: 'text2vec-cohere'
  COHERE_APIKEY: 'your-cohere-api-key'
  DEFAULT_VECTORIZER_MODULE: 'text2vec-cohere'
```

#### Local Transformers
```yaml
services:
  weaviate:
    environment:
      ENABLE_MODULES: 'text2vec-transformers'
      DEFAULT_VECTORIZER_MODULE: 'text2vec-transformers'
      TRANSFORMERS_INFERENCE_API: 'http://t2v-transformers:8080'
  
  t2v-transformers:
    image: semitechnologies/transformers-inference:sentence-transformers-multi-qa-MiniLM-L6-cos-v1
    environment:
      ENABLE_CUDA: '0'  # Set to '1' if you have GPU support
```

### 2. Generative Modules

#### OpenAI GPT
```yaml
environment:
  ENABLE_MODULES: 'text2vec-openai,generative-openai'
  OPENAI_APIKEY: 'your-openai-api-key'
```

#### Cohere Generate
```yaml
environment:
  ENABLE_MODULES: 'text2vec-cohere,generative-cohere'
  COHERE_APIKEY: 'your-cohere-api-key'
```

### 3. Multimodal Modules

#### CLIP for Images and Text
```yaml
services:
  weaviate:
    environment:
      ENABLE_MODULES: 'multi2vec-clip'
      DEFAULT_VECTORIZER_MODULE: 'multi2vec-clip'
      CLIP_INFERENCE_API: 'http://multi2vec-clip:8080'
  
  multi2vec-clip:
    image: semitechnologies/multi2vec-clip:sentence-transformers-clip-ViT-B-32-multilingual-v1
    environment:
      ENABLE_CUDA: '0'
```

## Environment Variables

### Core Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED` | `true` | Enable anonymous access |
| `AUTHENTICATION_APIKEY_ENABLED` | `false` | Enable API key authentication |
| `PERSISTENCE_DATA_PATH` | `./data` | Data storage path |
| `DEFAULT_VECTORIZER_MODULE` | `none` | Default vectorizer module |
| `ENABLE_MODULES` | `` | Comma-separated list of modules |
| `QUERY_DEFAULTS_LIMIT` | `25` | Default query limit |
| `QUERY_MAXIMUM_RESULTS` | `10000` | Maximum query results |

### Performance Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `GOMAXPROCS` | Auto | Number of CPU cores to use |
| `GOMEMLIMIT` | Auto | Memory limit for Go runtime |
| `PERSISTENCE_MEMTABLES_MAX_SIZE` | `200` | Max memtable size (MB) |
| `PERSISTENCE_MEMTABLES_FLUSH_IDLE_AFTER_SECONDS` | `60` | Flush idle timeout |

### Monitoring

| Variable | Default | Description |
|----------|---------|-------------|
| `PROMETHEUS_MONITORING_ENABLED` | `false` | Enable Prometheus metrics |
| `PROMETHEUS_MONITORING_PORT` | `2112` | Prometheus metrics port |
| `LOG_LEVEL` | `info` | Logging level (debug, info, warn, error) |
| `LOG_FORMAT` | `text` | Log format (text, json) |

### Clustering

| Variable | Default | Description |
|----------|---------|-------------|
| `CLUSTER_HOSTNAME` | Auto | Cluster node hostname |
| `CLUSTER_GOSSIP_BIND_PORT` | `7946` | Gossip protocol port |
| `CLUSTER_DATA_BIND_PORT` | `7947` | Data replication port |
| `RAFT_PORT` | `8300` | Raft consensus port |
| `RAFT_BOOTSTRAP_EXPECT` | `1` | Expected cluster size |

## Building from Source

### 1. Prerequisites

Ensure you have Go 1.22+ installed:

```bash
go version  # Should show 1.22 or higher
```

### 2. Clone and Build

```bash
# Clone repository
git clone https://github.com/weaviate/weaviate.git
cd weaviate

# Build Weaviate
make weaviate

# Or build with debug symbols
make weaviate-debug
```

### 3. Run Built Binary

```bash
# Run with default configuration
./weaviate --scheme http --host 127.0.0.1 --port 8080

# Run with custom configuration
./weaviate --config-file ./weaviate.conf.json
```

### 4. Cross-Platform Building

```bash
# Build for Linux
GOOS=linux GOARCH=amd64 make weaviate

# Build for macOS
GOOS=darwin GOARCH=amd64 make weaviate

# Build for Windows
GOOS=windows GOARCH=amd64 make weaviate
```

## Troubleshooting

### Common Issues

#### 1. Weaviate Won't Start

**Check logs:**
```bash
docker compose logs weaviate
```

**Common causes:**
- Insufficient memory
- Port conflicts
- Module configuration errors
- Corrupted data directory

#### 2. Module Connection Errors

**For external services (OpenAI, Cohere):**
- Verify API keys are correct
- Check internet connectivity
- Ensure sufficient API quotas

**For local modules:**
- Verify container is running: `docker compose ps`
- Check module logs: `docker compose logs t2v-transformers`

#### 3. Performance Issues

**Memory optimization:**
```yaml
environment:
  PERSISTENCE_MEMTABLES_MAX_SIZE: '100'
  PERSISTENCE_MEMTABLES_FLUSH_IDLE_AFTER_SECONDS: '30'
  LIMIT_RESOURCES: 'true'
```

**Query optimization:**
```yaml
environment:
  QUERY_DEFAULTS_LIMIT: '10'
  QUERY_MAXIMUM_RESULTS: '1000'
```

#### 4. Cluster Issues

**Check cluster status:**
```bash
curl http://localhost:8080/v1/nodes
```

**Common cluster problems:**
- Network connectivity between nodes
- Mismatched cluster configuration
- Split-brain scenarios

### Useful Commands

```bash
# Check Weaviate health
curl http://localhost:8080/v1/.well-known/ready

# View current configuration
curl http://localhost:8080/v1/meta

# Check cluster nodes
curl http://localhost:8080/v1/nodes

# View metrics (if enabled)
curl http://localhost:2112/metrics

# Backup data (S3 example)
curl -X POST http://localhost:8080/v1/backups/s3 \
  -H "Content-Type: application/json" \
  -d '{"id": "backup-1"}'
```

### Getting Help

If you encounter issues not covered here:

1. Check the [Weaviate Documentation](https://weaviate.io/developers/weaviate/)
2. Search existing [GitHub Issues](https://github.com/weaviate/weaviate/issues)
3. Join our [Community Slack](https://weaviate.io/slack)
4. Post on our [Community Forum](https://forum.weaviate.io)

For production support, consider [Weaviate Cloud Services](https://weaviate.io/cloud) for managed Weaviate instances.
