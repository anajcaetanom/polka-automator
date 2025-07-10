# Automation for PolKA Processes

This repository contains scripts and tools to automate tasks related to **PolKA** (Polynomial Key-based Architecture for Source Routing), using **Mininet** and **NetworkX**.

## 📌 About the Project

The main goal of this project is to simplify the manipulation of network topologies, as well as the simulation and testing of the PolKA architecture. It aims to reduce manual work when setting up test environments, routing logic, and other network-related operations.

## ⚙️ How To Use

### Creating the Virtual Machine

1. Download the Ubuntu 20.04 image:

    Available at: [Ubuntu website](https://releases.ubuntu.com/20.04.6/?_ga=2.149898549.2084151835.1707729318-1126754318.1683186906)

2. Use VirtualBox or VMware to create the VM.

### Installing PolKA dependencies

1. Update the OS:
    ```bash
    sudo apt update && sudo apt dist-upgrade -y
    ```
2. Clean installation files:
    ```bash
    sudo apt clean && sudo apt autoremove -y
    ```
3. Reboot the OS:
    ```bash
    sudo reboot
    ```
4. Install Mininet:
    ```bash
    sudo apt install mininet
    ```
5. Install Mininet Wifi:
    ```bash
    git clone https://github.com/intrig-unicamp/mininet-wifi
    cd mininet-wifi
    sudo util/install.sh -Wlnfv
    ```
6. Install P4C (P4 language compiler):
    ```bash
    source /etc/lsb-release
    sudo apt install curl
    echo "deb http://download.opensuse.org/repositories/home:/p4lang/xUbuntu_${DISTRIB_RELEASE}/ /" | sudo tee /etc/apt/sources.list.d/home:p4lang.list
    ```
    ```bash
    curl -fsSL https://download.opensuse.org/repositories/home:p4lang/xUbuntu_${DISTRIB_RELEASE}/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/home_p4lang.gpg > /dev/null
    ```
    ```bash
    sudo apt-get update
    sudo apt install p4lang-p4c
    ```
7. Install PolKA:
    ```bash
    pip install polka-routing
    ```

### Installing code dependencies

1. Install code requiriments:
    ```bash
    pip install -r requirements.txt
    ```

### Using the code
1. Run:
    ```bash
    sudo -E python3
    ```

2. Pick the option it better fits your needs:
    

## 🚀 Features (in progress)
