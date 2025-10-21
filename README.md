# Automation for PolKA Processes

This repository contains scripts and tools to automate tasks related to **PolKA** (Polynomial Key-based Architecture for Source Routing), using **Mininet** and **NetworkX**.

## About the Project

The main goal of this project is to simplify the manipulation of network topologies, as well as the simulation and testing of the PolKA architecture. It aims to reduce manual work when setting up test environments, routing logic, and other network-related operations.

## How To Use

1. clone the repository. branch: grpc-api

1. Install PolKA:
    ```bash
    $ pip install polka-routing
    ```

1. Install code requirements:
    ```bash
    $ pip install -r requirements.txt
    ```

### Using the code

1. Insert the p4 files in the polka folder; 

1. Navigate to the PolKA folder and run `make`:
    ```bash
    $ cd polka-automator/polka
    ```
    ```bash
    $ make
    ```

1. Insert the GML file in the "topologies" folder.
    
