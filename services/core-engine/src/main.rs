mod config;
mod models;
mod ingestion;
mod sql_guard;

use axum::{
    extract::{Multipart, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use chrono::Utc;
use serde_json::json;
use std::{net::SocketAddr, sync::Arc, time::Instant};
use tokio::sync::RwLock;
use tracing::{info, warn, Level};
use tracing_subscriber::FmtSubscriber;
use uuid::Uuid;

use crate::config::Config;
use crate::ingestion::TextExtractor;
use crate::models::{DocumentMetadata, IngestionStatus, SqlQueryRequest, SqlQueryResult};
use crate::sql_guard::SqlGuard;

// Application State shared across Axum handlers
#[derive(Clone)]
pub struct AppState {
    pub config: Config,
    pub documents: Arc<RwLock<Vec<DocumentMetadata>>>,
}

#[tokio::main]
async fn main() {
    // 1. Initialize structured logging with Tracing
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber)
        .expect("Failed to initialize tracing subscriber");

    // 2. Load Configuration
    let config = Config::from_env();
    info!("Starting ATLAS Core Engine on port {}", config.port);

    // 3. Shared State
    let state = AppState {
        config: config.clone(),
        documents: Arc::new(RwLock::new(Vec::new())),
    };

    // 4. Construct Axum Router
    let app = Router::new()
        .route("/health", get(health_handler))
        .route("/api/v1/documents/upload", post(upload_document_handler))
        .route("/api/v1/documents", get(list_documents_handler))
        .route("/api/v1/sql/execute", post(execute_sql_handler))
        .with_state(state);

    // 5. Start Server with Graceful Shutdown
    let addr = SocketAddr::from(([0, 0, 0, 0], config.port));
    let listener = tokio::net::TcpListener::bind(addr)
        .await
        .expect("Failed to bind port");

    info!("ATLAS Core Engine listening on http://{}", addr);

    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await
        .expect("Server error");
}

// Health Handler
async fn health_handler() -> impl IntoResponse {
    (
        StatusCode::OK,
        Json(json!({
            "status": "UP",
            "service": "atlas-core-engine",
            "engine": "Rust (Tokio + Axum)",
            "version": env!("CARGO_PKG_VERSION")
        })),
    )
}

// Upload & Process Document Handler
async fn upload_document_handler(
    State(state): State<AppState>,
    mut multipart: Multipart,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
    while let Some(field) = multipart.next_field().await.map_err(|e| {
        (
            StatusCode::BAD_REQUEST,
            Json(json!({ "error": format!("Multipart error: {}", e) })),
        )
    })? {
        let filename = field
            .file_name()
            .unwrap_or("document.txt")
            .to_string();

        let data = field.bytes().await.map_err(|e| {
            (
                StatusCode::BAD_REQUEST,
                Json(json!({ "error": format!("Byte read error: {}", e) })),
            )
        })?;

        let sha256 = TextExtractor::compute_sha256(&data);

        // Check for duplicate document
        {
            let docs = state.documents.read().await;
            if let Some(existing) = docs.iter().find(|d| d.sha256_hash == sha256) {
                return Ok((
                    StatusCode::OK,
                    Json(json!({
                        "message": "Duplicate document detected via SHA-256 integrity hash",
                        "document": existing,
                        "is_duplicate": true
                    })),
                ));
            }
        }

        let text_content = String::from_utf8_lossy(&data).to_string();
        let doc_id = Uuid::new_v4();
        let chunks = TextExtractor::chunk_text(doc_id, &text_content, 800, 150);

        let metadata = DocumentMetadata {
            id: doc_id,
            filename: filename.clone(),
            file_type: filename.split('.').last().unwrap_or("unknown").to_string(),
            file_size_bytes: data.len(),
            sha256_hash: sha256,
            status: IngestionStatus::Completed,
            chunk_count: chunks.len(),
            created_at: Utc::now(),
        };

        {
            let mut docs = state.documents.write().await;
            docs.push(metadata.clone());
        }

        info!(
            "Document ingested successfully: {} ({} chunks created)",
            filename,
            chunks.len()
        );

        return Ok((
            StatusCode::CREATED,
            Json(json!({
                "message": "Document successfully ingested and indexed",
                "document": metadata,
                "is_duplicate": false
            })),
        ));
    }

    Err((
        StatusCode::BAD_REQUEST,
        Json(json!({ "error": "No file field found in form" })),
    ))
}

// List Documents Handler
async fn list_documents_handler(State(state): State<AppState>) -> impl IntoResponse {
    let docs = state.documents.read().await;
    (StatusCode::OK, Json(json!({ "count": docs.len(), "documents": *docs })))
}

// Controlled SQL Gateway Handler
async fn execute_sql_handler(
    Json(payload): Json<SqlQueryRequest>,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
    let start = Instant::now();

    // Enforce AST-level read-only constraint
    if let Err(err_msg) = SqlGuard::validate_read_only(&payload.query) {
        warn!("Blocked unsafe SQL execution attempt: {}", err_msg);
        return Err((
            StatusCode::FORBIDDEN,
            Json(json!({
                "error": "Query rejected by ATLAS SQL Guard",
                "reason": err_msg
            })),
        ));
    }

    // Simulated approved structured database query return
    let sample_records = vec![
        json!({ "department": "Marketing", "allocated_budget": 500000, "actual_spend": 620000, "variance": 120000 }),
        json!({ "department": "Engineering", "allocated_budget": 1200000, "actual_spend": 1340000, "variance": 140000 }),
    ];

    let execution_time_ms = start.elapsed().as_millis();

    Ok((
        StatusCode::OK,
        Json(SqlQueryResult {
            query: payload.query,
            rows_affected: sample_records.len() as u64,
            execution_time_ms,
            records: sample_records,
        }),
    ))
}

// Graceful Shutdown Signal Handler
async fn shutdown_signal() {
    tokio::signal::ctrl_c()
        .await
        .expect("Failed to install Ctrl+C handler");
    info!("Shutdown signal received. Finishing pending tasks...");
}
