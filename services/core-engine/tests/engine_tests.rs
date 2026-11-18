#[cfg(test)]
mod tests {
    use core_engine::ingestion::TextExtractor;
    use core_engine::sql_guard::SqlGuard;
    use uuid::Uuid;

    #[test]
    fn test_sha256_hash_computation() {
        let content = b"Enterprise financial ledger report Q3";
        let hash1 = TextExtractor::compute_sha256(content);
        let hash2 = TextExtractor::compute_sha256(content);
        assert_eq!(hash1, hash2);
        assert_eq!(hash1.len(), 64);
    }

    #[test]
    fn test_text_chunking() {
        let doc_id = Uuid::new_v4();
        let sample = "Paragraph 1: Budget allocation exceeded. Paragraph 2: Cloud infrastructure scaling drove 40% of variance.";
        let chunks = TextExtractor::chunk_text(doc_id, sample, 40, 10);
        assert!(chunks.len() >= 2);
        assert_eq!(chunks[0].document_id, doc_id);
        assert!(chunks[0].token_estimate > 0);
    }

    #[test]
    fn test_sql_guard_allows_safe_select() {
        let query = "SELECT department, actual_spend FROM budgets WHERE variance > 50000";
        assert!(SqlGuard::validate_read_only(query).is_ok());
    }

    #[test]
    fn test_sql_guard_rejects_destructive_statements() {
        let drop_query = "DROP TABLE departments;";
        assert!(SqlGuard::validate_read_only(drop_query).is_err());

        let delete_query = "DELETE FROM budgets WHERE 1=1";
        assert!(SqlGuard::validate_read_only(delete_query).is_err());

        let update_query = "UPDATE budgets SET actual_spend = 0";
        assert!(SqlGuard::validate_read_only(update_query).is_err());

        let multi_statement = "SELECT 1; DROP TABLE budgets;";
        assert!(SqlGuard::validate_read_only(multi_statement).is_err());
    }
}
