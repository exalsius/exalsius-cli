# exalsius CLI
<p align="center">                                                                                                                                                                            
  <img src="docs/assets/logo.png" alt="Exalsius Logo" width="300"/>                                                                                                                           
</p>                                                                                                                                                                                               
exalsius CLI (`exalsius`) is a command-line tool designed for orchestrating and managing distributed AI training workloads. As part of the Exalsius stack, it enables seamless deployment and execution of AI training jobs on ephemeral clusters across multiple cloud providers and hyperscalers, referred to as "colonies". A colony may consist of one or more GPU clusters, deployed across a single or multiple cloud providers, optimizing flexibility and scalability.


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
uv pip install .
```

## Usage

### Prerequisites
To use the exalsius CLI, ensure the following requirements are met:

- You must have access to a Kubernetes cluster where the exalsius-operator is deployed. This can be a local deployment (e.g., using Kind) or a remote cluster.
- You must have access to the cluster via a kubeconfig file. The file should either be located at `~/.kube/config` or specified using the `KUBECONFIG` environment variable.

- The following environment variable must be set to authenticate with the SkyPilot API server, which is deployed as part of the exalsius-operator:

```bash
export SKYPILOT_API_SERVER_ENDPOINT=http://<user>:<password>@127.0.0.1:30050
```

After installation, the `exalsius` command is available in your shell. Below is the general usage pattern:

```bash
exalsius [OPTIONS] COMMAND [ARGS]...
```

### Global Options

| Option                  | Shortcut | Description                              |
|-------------------------|----------|------------------------------------------|
| `--version`            | `-v`     | Show the version and exit.              |
| `--install-completion` |          | Install shell completion.               |
| `--show-completion`    |          | Show shell completion script.           |
| `--help`               |          | Show help message and exit.             |

### Commands

| Command       | Description                                                        |
|--------------|--------------------------------------------------------------------|
| `clouds`     | List available configured cloud providers.                        |
| `scan-prices`| Scan and compare GPU prices across cloud providers.              |
| `jobs`       | List and create training jobs.                                    |
| `colonies`   | List and create exalsius colonies (ephemeral training clusters). |

## Examples

### List Available Cloud Providers
```bash
exalsius clouds list
```

### Scan GPU Prices Across Cloud Providers
```bash
exalsius scan-prices list-gpus --gpu A100 --clouds AWS
```

#### Example Output:
```
                                                           A100                                                            
┏━━━━━━┳━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ GPU  ┃ QTY ┃ CLOUD ┃ INSTANCE_TYPE ┃ DEVICE_MEM ┃ vCPUs ┃ HOST_MEM ┃ HOURLY_PRICE ┃ HOURLY_SPOT_PRICE ┃ REGION         ┃
┡━━━━━━╇━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ A100 │ 8   │ AWS   │ p4d.24xlarge  │ 40GB       │ 96    │ 1152GB   │ $ 32.773     │ $ 8.265           │ us-east-1      │
│ A100 │ 8   │ AWS   │ p4d.24xlarge  │ 40GB       │ 96    │ 1152GB   │ $ 32.773     │ $ 8.407           │ us-east-2      │
│ A100 │ 8   │ AWS   │ p4d.24xlarge  │ 40GB       │ 96    │ 1152GB   │ $ 32.773     │ $ 9.906           │ us-west-2      │
│ A100 │ 8   │ AWS   │ p4d.24xlarge  │ 40GB       │ 96    │ 1152GB   │ $ 35.397     │ $ 18.021          │ eu-west-1      │
│ A100 │ 8   │ AWS   │ p4d.24xlarge  │ 40GB       │ 96    │ 1152GB   │ $ 39.320     │ -                 │ ap-south-1     │
└──────┴─────┴───────┴───────────────┴────────────┴───────┴──────────┴──────────────┴───────────────────┴────────────────┘
```

### Create a New AI Training Job
```bash
exalsius jobs create --config job-config.yaml
```

## Integration with Exalsius Operator
exalsius CLI is designed to work seamlessly with the [exalsius operator](https://github.com/exalsius/exalsius-operator), which manages AI workloads and infrastructure within Kubernetes clusters.

## Contributing
Contributions are welcome! Please check out our contribution guidelines.


## Contact
For questions or support, please open an issue on the repository.

