use serde::Serialize;
use std::fmt;

/// Error types for agent operations
#[derive(Debug)]
pub enum AgentError {
    ApiError(String),
    ParseError(String),
    ToolNotFound(String),
    Cancelled,
}

impl fmt::Display for AgentError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AgentError::ApiError(msg) => write!(f, "API error: {}", msg),
            AgentError::ParseError(msg) => write!(f, "Parse error: {}", msg),
            AgentError::ToolNotFound(name) => write!(f, "Tool not found: {}", name),
            AgentError::Cancelled => write!(f, "Agent execution cancelled"),
        }
    }
}

impl std::error::Error for AgentError {}

/// Represents a message in the conversation history
#[derive(Debug, Clone)]
pub enum Message {
    User {
        content: String,
    },
    Assistant {
        content: Vec<ContentBlock>,
    },
    ToolResult {
        tool_use_id: String,
        content: String,
    },
}

/// Content blocks within assistant messages
#[derive(Debug, Clone)]
pub enum ContentBlock {
    Text {
        text: String,
    },
    ToolUse {
        id: String,
        name: String,
        input: serde_json::Value,
    },
}

/// Tool definition for Claude API
#[derive(Debug, Clone, Serialize)]
pub struct Tool {
    pub name: String,
    pub description: String,
    pub input_schema: serde_json::Value,
}

/// Type alias for tool implementation functions
pub type ToolFn = Box<dyn Fn(serde_json::Value) -> Result<String, String> + Send + Sync>;
