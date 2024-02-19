use redis::Commands;
use serde::{Deserialize, Serialize};

const LOCAL_REDIS_URL: &str = "redis://127.0.0.1:6379";
const UPSTASH_REDIS_URL: &str =
    "redis://default:d0ac64668d6e43cea9c1c4fe13f8e60f@fly-transcription_tasks.upstash.io:6379";
const REDIS_TASK_QUEUE_NAME: &str = "transcription_task_queue";

#[derive(Serialize, Deserialize, Debug)]
struct TranscriptionTask {
    id: u32,
    video_id: Vec<String>,
}

pub fn push_transcription_task_to_queue() -> redis::RedisResult<()> {
    let redis_client = redis::Client::open(LOCAL_REDIS_URL)?;
    let mut conn = redis_client.get_connection()?;
    println!("Connected to Redis queue!");

    // TODO: Read from file and create a task from each video/playlist link
    let test_transcription_task = TranscriptionTask {
        id: 1,
        video_id: vec!["https://www.youtube.com/watch?v=swJsw9Jvgoc".to_string()],
    };
    let serialized_transcription_task = serde_json::to_string(&test_transcription_task).unwrap();

    let res = conn.lpush(REDIS_TASK_QUEUE_NAME, serialized_transcription_task)?;
    println!(
        "Task: {:?} successfully pushed onto queue: {:?}!",
        test_transcription_task, res
    );
    Ok(())
}
