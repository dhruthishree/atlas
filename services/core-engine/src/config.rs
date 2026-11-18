use std::env;

#[derive(Clone, Debug)]
pub struct Config {
    pub port: u16,
    pub environment: String,
    pub database_url: String,
    pub ai_orchestrator_url: String,
}

impl Config {
    pub fn from_env() -> Self {
        Self {
            port: env::var("PORT")
                .unwrap_or_else(|_| "8080".to_string())
                .parse::<u16>()
                .unwrap_or(8080),
            environment: env::var("ENVIRONMENT").unwrap_or_else(|_| "development".to_string()),
            database_url: env::var("DATABASE_URL").unwrap_or_else(|_| "sqlite://atlas.db?mode=rwc".to_string()),
            ai_orchestrator_url: env::var("AI_ORCHESTRATOR_URL").unwrap_or_else(|_| "http://localhost:8002".to_string()),
        }
    }
}
