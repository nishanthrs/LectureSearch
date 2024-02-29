# Typesense Search Index 

## Setup on Fly.io

* Was planning to start this on the same VM as the backend, but it seems like you can't do that via Fly.io :/
* I guess the side benefit is that I can scale the Typesense cluster independent of my search backend service, but still annoying I have to overengineer this much to get a simple prototype up and running
* Here are the steps I took to set this up:
  * Removed all typesense setup on search backend Dockerfile
  * Setup basic fly.toml: `fly launch`
  * Create a fly volume: `fly vol create typesense_data -r ewr`
    * [Fly volume docs](https://fly.io/docs/reference/volumes/)
  * Modified mounts in fly.toml and used pre-built Typesense Docker image
  * Fly's private networking relies on programs listening on IPv6 addresses, but Typesense only support IPv4. Use flycast to route connections through a proxy that can handle IPv4: `fly ips allocate-v6 --private`
    * Found this issue in [the forums](https://community.fly.io/t/cant-connect-to-typesense-deployment-via-private-network/12662/5)
  * Deploy via `fly deploy`
  * Test connection to b/w Fly.io apps using [this guide](https://fly.io/docs/networking/private-networking/#flycast-private-load-balancing)
* Other guides:
  * [Database and Storage Fly.io Guide](https://fly.io/docs/database-storage-guides/)