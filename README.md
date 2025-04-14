# CECS327-Project-3

# Project 3: Distribution and Scalability

# Overview 

This project extends the previous peer-to-peer (P2P) network via Docker containers. You will enhance
your P2P network to support decentralized storage and retrieval. Each node will be able to:

• Upload and download files
• Insert and query key-value pairs
• Distribute storage responsibilities using a basic Distributed Hash Table (DHT)

This phase introduces data layer concepts essential for scalable, decentralized systems.

## ** Project Files **

- "p2p-node" which contains: 
    - A folder named 'storage'
    - app.py
    - Dockerfile
    - mydoc.txt


## **Installation Instructions **

### **Step 1: Install Docker**

Ensure that Docker is installed on your system. You can download it from:

- [Docker for Windows/macOS](https://www.docker.com/products/docker-desktop)
- [Docker for Linux](https://docs.docker.com/engine/install/)

Verify the installation:

```bash
docker --version
docker run hello-world
```

---

## **Compiling and Running the Application**

## --- Phase 1 ---

### **Step 2: Build the docker image**

Navigate to the p2p-node file. Run the following command to build the docker image 

```
    docker build -t p2p-node .
```

### **Step 3: Run the container with volume mounting**

Use the following command to start the container and mount a volume for shared file persistence: 

```
docker run -d -p 5001:5000 -v "$(pwd)/storage:/app/storage" --name node1 p2p-node

```

### **Step 4: Upload a file via curl **

Use the following command to upload "mydoc.txt" 

```
curl.exe -F 'file=@mydoc.txt' http://localhost:5001/upload

```

### **Step 5: Download the file **

Go to your browser and visit the following URL to download our uploaded file: 

```
http://localhost:5001/download/mydoc.txt

```

## --- Phase 2 ---

### **Step 6: **



