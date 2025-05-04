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

Within the command terminal, enter the following command to send a key-alue dictionary pair to be remembered by the docker containers using windows powershell 

```
    Invoke-RestMethod -Uri http://localhost:5001/kv -Method POST -Headers @{ "Content-Type" = "application/json" } -Body '{"key":"color","value":"blue"}'
```

To check to make sure the information was succesfully saved you can get the information using this line
```
    Invoke-RestMethod -Uri http://localhost:5001/kv/color -Method GETInvoke-RestMethod -Uri http://localhost:5001/kv/color -Method GET

    # OR use command 

    http://localhost:5001/kv/color
```

## --- Phase 3 ---

### **Step 7: Launch Multi-Node Network with Docker Compose**

Use the provided `docker-compose.yml` to start a bootstrap server and 12 peer nodes:

```powershell
docker-compose up --build --scale node=12
```

### **Step 8: Store and Query a Key-Value Pair Across the Network**

#### 🔹 Windows (PowerShell)

Store a key-value pair on Node 1 using `Invoke-RestMethod`:

```powershell
Invoke-RestMethod -Uri http://localhost:5001/kv -Method POST -Headers @{ "Content-Type" = "application/json" } -Body '{"key":"color","value":"blue"}'
```

Query all 12 nodes to check which one stores the key:

```powershell
For ($i = 1; $i -le 12; $i++) {
    $port = 5000 + $i
    Write-Host "`n[Node $i - Port $port]"
    try {
        Invoke-RestMethod -Uri http://localhost:$port/kv/color -Method GET
    } catch {
        Write-Host "No response or key not found."
    }
}
```

---

#### 🔹 Linux/macOS (or WSL)

Store the key-value pair using `curl`:

```bash
curl -X POST http://localhost:5001/kv -H "Content-Type: application/json" -d '{"key":"color","value":"blue"}'
```

Query each node with a loop:

```bash
for i in {1..12}; do
  port=$((5000 + i))
  echo -e "\n[Node $i - Port $port]"
  curl http://localhost:$port/kv/color
done
```
```

