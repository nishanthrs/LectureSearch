mod transcription_tasks;

use anyhow::{Error, Result};
use axum::{extract::Query, http::StatusCode, routing::get, Json, Router};
use serde::de::value::MapDeserializer;
use serde::{Deserialize, Serialize};
use std::env;
use std::net::SocketAddr;
use typesense_codegen::apis::configuration::{ApiKey, Configuration};
use typesense_codegen::apis::documents_api::search_collection;
use typesense_codegen::models::SearchParameters;
use url::Url;

use transcription_tasks::push_transcription_task_to_queue;

// TODO: Separate out SQLite and Typesense DBs into separate Fly.io apps

#[derive(Deserialize)]
struct SearchParams {
    query: String,
}

#[derive(Deserialize)]
struct UploadParams {
    video_url: String,
}

#[derive(Serialize)]
struct SearchReqParams {
    q: String,
    query_by: String,
    sort_by: String,
    page: i32,
    per_page: i32,
}

#[derive(Serialize, Deserialize, Debug)]
struct VideoTranscriptionDoc {
    channel: String,
    channel_follower_count: i32,
    content: String,
    end_time: i32,
    id: String,
    like_count: i32,
    start_time: i32,
    title: String,
    upload_date: String,
    video_id: String,
    view_count: i32,
}

async fn search_typesense_idx(query: String) -> Result<Vec<VideoTranscriptionDoc>> {
    let client = reqwest::Client::new();
    let typesense_host = Url::parse("https://typesense-search-idx.fly.dev").unwrap();
    let collection_name = "educational_video_transcriptions";
    let typesense_config = Configuration {
        base_path: typesense_host.to_string(),
        client,
        api_key: Some(ApiKey {
            prefix: None,
            key: env::var("TYPESENSE_API_KEY").unwrap(),
        }),
        basic_auth: None,
        oauth_access_token: None,
        bearer_access_token: None,
        user_agent: None,
    };
    let typesense_search_params = SearchParameters {
        q: query.clone(),
        query_by: "content".to_string(),
        sort_by: Some("start_time:asc".to_string()),
        page: Some(1),
        per_page: Some(25),
        ..Default::default()
    };

    let search_response =
        search_collection(&typesense_config, collection_name, typesense_search_params).await?;
    match search_response.hits {
        Some(hits) => {
            println!("Got {} hits", hits.len());
            for hit in &hits {
                println!("Hit: {:?}", hit);
            }
            let video_docs = hits
                .iter()
                .filter_map(|hit| match &hit.document {
                    Some(doc) => Some(
                        // TODO: Look into better ways of deserializing HashMap<String, serde_json::Value> into VideoTranscriptionDoc
                        // https://www.google.com/search?q=convert+hashmap+to+serde_json%3A%3AMap
                        VideoTranscriptionDoc::deserialize(MapDeserializer::new(
                            doc.clone().into_iter(),
                        ))
                        .unwrap(),
                    ),
                    // Should not happen due to skip_serializing_if macro in SearchResultHit struct
                    None => None,
                })
                .collect();
            Ok(video_docs)
        }
        None => Ok(vec![]),
    }
}

async fn handle_search(
    Query(search_params): Query<SearchParams>,
) -> (StatusCode, Json<Vec<VideoTranscriptionDoc>>) {
    let video_docs = search_typesense_idx(search_params.query).await.unwrap();
    println!("Video docs: {:?}", video_docs);
    (StatusCode::OK, Json(video_docs))
}

async fn upload_transcriptions_to_search_idx(video_url: String) -> Result<(), Error> {
    push_transcription_task_to_queue(video_url)
}

async fn handle_upload(Query(upload_params): Query<UploadParams>) -> (StatusCode, String) {
    let _ = upload_transcriptions_to_search_idx(upload_params.video_url)
        .await
        .unwrap();
    (StatusCode::OK, "Successfully uploaded!".to_string())
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/search", get(handle_search))
        .route("/upload", get(handle_upload));
    let addr = "[::]:8080".parse::<SocketAddr>().unwrap();
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
}
