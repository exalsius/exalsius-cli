<p align="middle"><img src="./docs/assets/logo_banner.png" alt="exalsius banner" width="250"></p>

<h1 align="center">exalsius CLI (`exls`)</h1>

<div align="center">

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) ![CI](https://img.shields.io/github/actions/workflow/status/exalsius/exalsius-cli/ci.yml?label=CI)

</div>

The exalsius CLI (`exls`) is a command-line tool for orchestrating and managing distributed AI training workloads on ephemeral clusters.
As a core component of the exalsius stack, it enables deployment and management of AI training jobs across multiple cloud providers and on-premise hardware.

## Features

- **Cluster Management:** Deploy, manage, and scale ephemeral clusters for your AI workloads.
- **Node Management:** Easily add and manage nodes from different cloud providers or your own hardware.
- **Cost-Aware GPU Selection:** Scan for GPU prices across cloud providers to find the most cost-effective options.
- **Workspace Orchestration:** Create and manage various types of workspaces, such as Jupyter, DevPod, and more, on your clusters.
- **Extensible and Cloud-Agnostic:** Designed to be flexible and work with a variety of cloud providers.

## Getting Started

### Prerequisites

- Python 3.12 or newer.

### Installation

It is recommended to install `exls` in a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

You can install the CLI using `pip` or `uv`:

**With pip:**

```bash
pip install git+https://github.com/exalsius/exalsius-cli.git@main
```

**With uv:**

```bash
uv pip install git+https://github.com/exalsius/exalsius-cli.git@main
```

To verify the installation, run:

```bash
exls --help
```

## Usage

### Login

Before you can use the CLI, you need to authenticate with your exalsius account:

```bash
exls login
```

### Core Commands

Here are some of the core commands to get you started:

- **`exls offers`**: Find the best GPU deals.
  - `exls offers list --gpu-type "H100"`: List all offers for H100 GPUs.
- **`exls nodes`**: Manage the nodes in your node pool.
  - `exls nodes import-offer <offer-id>`: Import a node from a cloud provider offer.
  - `exls nodes list`: List all available nodes.
- **`exls clusters`**: Manage your clusters.
  - `exls clusters deploy --interactive`: Interactively create a new cluster.
  - `exls clusters list`: List all your clusters.
  - `exls clusters get <cluster-id>`: Get details for a specific cluster.
- **`exls workspaces`**: Manage workspaces on your clusters.
  - `exls workspaces deploy jupyter <cluster-id>`: Deploy a Jupyter workspace on a cluster.
  - `exls workspaces list <cluster-id>`: List workspaces on a cluster.

For more details on each command, you can use the `--help` flag, for example `exls clusters --help`.

## Documentation

For more in-depth information and advanced usage, please refer to our official documentation.

- **[Full Documentation](https://docs.exalsius.com)**
- **[API Reference](https://api.exalsius.ai/docs)**

## Community & Support

- Join our **[Discord server](https://discord.gg/nsMymbvNZk)** to chat with us.
- If you encounter any bugs or have feature requests, please open an issue on our **[GitHub repository](https://github.com/exalsius/exalsius-cli/issues)**.

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.
