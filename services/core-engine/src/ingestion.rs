use sha2::{Digest, Sha256};
use uuid::Uuid;
use crate::models::DocumentChunk;

pub struct TextExtractor;

impl TextExtractor {
    pub fn compute_sha256(bytes: &[u8]) -> String {
        let mut hasher = Sha256::new();
        hasher.update(bytes);
        format!("{:x}", hasher.finalize())
    }

    pub fn chunk_text(doc_id: Uuid, text: &str, chunk_size: usize, overlap: usize) -> Vec<DocumentChunk> {
        let mut chunks = Vec::new();
        let characters: Vec<char> = text.chars().collect();
        let total_len = characters.len();

        if total_len == 0 {
            return chunks;
        }

        let mut start = 0;
        let mut index = 0;

        while start < total_len {
            let end = (start + chunk_size).min(total_len);
            let slice: String = characters[start..end].iter().collect();
            let trimmed = slice.trim().to_string();

            if !trimmed.is_empty() {
                let token_estimate = (trimmed.len() / 4).max(1);
                chunks.push(DocumentChunk {
                    id: Uuid::new_v4(),
                    document_id: doc_id,
                    chunk_index: index,
                    content: trimmed,
                    token_estimate,
                });
                index += 1;
            }

            if end == total_len {
                break;
            }
            start += chunk_size.saturating_sub(overlap);
        }

        chunks
    }
}
