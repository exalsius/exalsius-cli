<h1 align="center">
  <br>
  <img height="300" src="docs/assets/logo.png"> <br>
    exalsius-cli
<br>
</h1>
                                                                                                                                                                                           
exalsius CLI (`exls`) is a command-line tool designed for orchestrating and managing distributed AI training workloads. As part of the Exalsius stack, it enables seamless deployment and execution of AI training jobs on ephemeral clusters across multiple cloud providers and hyperscalers, referred to as "colonies". A colony may consist of one or more GPU clusters, deployed across a single or multiple cloud providers, optimizing flexibility and scalability.

In addition to workload orchestration, exalsius CLI provides GPU price scanning and comparison across various public cloud platforms and hyperscalers, empowering users to identify the most cost-effective resources for their AI training workloads.

## Features

- **Orchestration of distributed AI training**
- **Ephemeral cluster creation across multiple cloud providers** ("colonies")
- **Cost-aware GPU instance selection** through price scanning
- **Integration with [exalsius operator](https://github.com/exalsius/exalsius-operator)**
- **Extensible and cloud-agnostic**

## Installation

exalsius CLI requires Python 3.12. It can be installed using `pip` or `uv`:

### Using `pip`:
```bash
git clone https://github.com/exalsius/exalsius-cli.git
cd exalsius-cli
pip install -e .
```

### Using `uv`:
```bash
git clone https://github.com/exalsius/exalsius-cli.git
cd exalsius-cli
uv pip install -e .
```

## Usage

### Prerequisites
Currently, the API is protected by basic authentication. Before using the CLI, ensure you have set the `EXALSIUS_USERNAME` and `EXALSIUS_PASSWORD` environment variables with the exalsius credentials.

