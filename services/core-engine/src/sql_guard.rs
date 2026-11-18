pub struct SqlGuard;

impl SqlGuard {
    /// Validates whether a SQL query is strictly read-only and safe to execute.
    /// Rejects destructive operations like DROP, TRUNCATE, DELETE, UPDATE, ALTER, INSERT.
    pub fn validate_read_only(sql: &str) -> Result<(), String> {
        let normalized = sql.trim().to_uppercase();

        // Must start with SELECT or WITH (for Common Table Expressions)
        if !normalized.starts_with("SELECT") && !normalized.starts_with("WITH") {
            return Err("Execution rejected: only SELECT queries are permitted.".to_string());
        }

        // Dangerous statement keywords
        let forbidden_keywords = [
            "DROP ", "TRUNCATE ", "DELETE ", "UPDATE ", "ALTER ", 
            "INSERT ", "GRANT ", "REVOKE ", "EXEC ", "EXECUTE ", "--", "/*"
        ];

        for keyword in forbidden_keywords {
            if normalized.contains(keyword) {
                return Err(format!("Security violation: query contains prohibited token '{}'", keyword));
            }
        }

        // Must not contain multiple statements (semicolon injection check)
        let trimmed_semicolons = normalized.trim_end_matches(';').trim();
        if trimmed_semicolons.contains(';') {
            return Err("Security violation: multiple semicolon-delimited SQL statements are forbidden.".to_string());
        }

        Ok(())
    }
}
