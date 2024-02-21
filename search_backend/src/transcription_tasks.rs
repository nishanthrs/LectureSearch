use std::time::SystemTime;

use anyhow::Result;
use redis::Commands;
use rusqlite::Connection;
use serde::{Deserialize, Serialize};

const LOCAL_REDIS_URL: &str = "redis://127.0.0.1:6379";
const UPSTASH_REDIS_URL: &str =
    "redis://default:dc4072d39b6745739f01b6c14cc2a658@fly-lecturesearch-web-redis.upstash.io:6379";
const REDIS_TASK_QUEUE_NAME: &str = "transcription_task_queue";

#[derive(Serialize, Deserialize, Debug)]
struct TranscriptionTask {
    id: u32,
    video_url: String,
}

pub fn push_transcription_task_to_queue(video_url: String) -> Result<()> {
    let redis_client = redis::Client::open(UPSTASH_REDIS_URL).unwrap();
    let mut redis_conn = redis_client.get_connection().unwrap();
    println!("Connected to Redis queue on {}!", UPSTASH_REDIS_URL);

    // let video_url = "https://www.youtube.com/watch?v=swJsw9Jvgoc";
    let curr_ts = SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .unwrap()
        .as_secs();
    let sqlite_conn = Connection::open("lecturesearch.db").unwrap();
    let table_creation_res = sqlite_conn.execute(
        "CREATE TABLE IF NOT EXISTS processed_videos (
            video_url TEXT PRIMARY KEY,
            processed_timestamp INTEGER NOT NULL
        )",
        (),
    );
    println!("Table creation res: {}", table_creation_res.unwrap());

    let mut find_video_statement =
        sqlite_conn.prepare("SELECT * FROM processed_videos WHERE video_url = ?1")?;
    let mut find_video_rows = find_video_statement.query([&video_url])?;
    while let Ok(Some(row)) = find_video_rows.next() {
        let video_processed_ts: i64 = row.get("processed_timestamp").unwrap();
        println!(
            "Video: {} was already processed at {}. Will not add to Redis task queue.",
            video_url, video_processed_ts
        );
        return Ok(());
    }
    let num_rows = sqlite_conn.execute(
        "INSERT INTO processed_videos (video_url, processed_timestamp) VALUES (?1, ?2)",
        (&video_url, curr_ts),
    );
    println!("Number of inserted rows: {}", num_rows.unwrap());

    let test_transcription_task = TranscriptionTask {
        id: 1,
        video_url: video_url,
    };
    let serialized_transcription_task = serde_json::to_string(&test_transcription_task).unwrap();
    let _ = redis_conn.lpush(REDIS_TASK_QUEUE_NAME, serialized_transcription_task)?;
    println!(
        "Task: {:?} successfully pushed onto queue!",
        test_transcription_task
    );
    Ok(())
}
