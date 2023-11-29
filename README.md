# LectureSearch

Website to help you find spoken words
Dataset v1 consists of MIT OCW videos for course 6 (Electrical Engineering & Computer Science) and 18 (Mathematics).

## Structure
1. Backend Web Server
  * Written in Rust on Axum web framework
2. Frontend
  * Written via NextJS framework
3. ETL Pipeline 
  * Will be productionized as either Airflow or Windmill async job / pipeline
  * Will be deployed and run on Kubernetes workers
  * TODO: Deploy on [GPU cloud](https://vast.ai/docs/overview/introduction) and run via [FasterWhisper framework](https://github.com/SYSTRAN/faster-whisper)

## System Design

TODO
