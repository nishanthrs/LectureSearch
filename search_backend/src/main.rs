use axum::{extract::Query, routing::get, Router};
use reqwest::header::{HeaderMap, CONTENT_TYPE};
use serde::{Serialize, Deserialize};
use serde_json::json;
use std::net::SocketAddr;
use url::Url;

#[derive(Deserialize)]
struct SearchParams {
    query: String,
}

#[derive(Serialize, Deserialize)]
struct TypesenseSearchParams {
    q: String,
    query_by: String,
    sort_by: String,
    page: u32,
    per_page: u32,
}

async fn search_typesense_idx(query: String) {
    let client = reqwest::Client::new();
    let mut headers = HeaderMap::new();
    headers.insert(CONTENT_TYPE, "application/json".parse().unwrap());
    headers.insert("X-TYPESENSE-API-KEY", "xyz".parse().unwrap());
    let typesense_host = Url::parse("http://127.0.0.1:8108").unwrap();
    println!("Typesense host: {}", typesense_host);
    let collection_name = "educational_video_transcriptions";
    let search_query_json = json!(
        {"q": query, "query_by": "content", "sort_by": "start_time:asc", "page": 1, "per_page": 25}
    );
    // let search_query = TypesenseSearchParams {
    //     q: query,
    //     query_by: "content".to_string(),
    //     sort_by: "start_time:asc".to_string(),
    //     page: 1,
    //     per_page: 25,
    // };
    let search_query_params = [
        ("q", query.as_str()),
        ("query_by", "content"),
        ("sort_by", "start_time:asc"),
        ("page", "1"),
        ("per_page", "25"),
    ];
    println!("Search request: {:?}", search_query_json);
    println!("Searching with: {}", query);
    let search_response = client.get(format!("{}/collections/{}/documents/search", typesense_host, collection_name))
        .headers(headers)
        .query(&search_query_params)
        .send()
        .await
        .expect(format!("Failed to get search response from Typesense idx for query: {}", query).as_str());
    println!("Search response status: {}", search_response.status());
    // let search_response_json = search_response.json().await.expect("Failed to parse search response as JSON.");
    println!("{:?}", search_response.text().await.unwrap());
}

async fn handler(Query(search_params): Query<SearchParams>) -> String {
    search_typesense_idx(search_params.query).await;
    "HELLO".to_string()
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/", get(handler));
    let addr = SocketAddr::from(([127, 0, 0, 1], 42069));

    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
}
