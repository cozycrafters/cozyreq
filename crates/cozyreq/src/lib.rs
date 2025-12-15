pub mod tui;

use std::fmt;

/// Represents a single HTTP request in the execution flow
#[derive(Debug, Clone, PartialEq)]
pub struct ExecutionRequest {
    pub number: usize,
    pub method: String,
    pub url: String,
    pub headers: Vec<(String, String)>,
    pub body: Option<String>,
    pub status_code: Option<u16>,
    pub response_body: Option<String>,
    pub duration_ms: Option<u64>,
}

impl ExecutionRequest {
    pub fn new(number: usize, method: String, url: String) -> Self {
        Self {
            number,
            method,
            url,
            headers: Vec::new(),
            body: None,
            status_code: None,
            response_body: None,
            duration_ms: None,
        }
    }

    pub fn with_headers(mut self, headers: Vec<(String, String)>) -> Self {
        self.headers = headers;
        self
    }

    pub fn with_body(mut self, body: String) -> Self {
        self.body = Some(body);
        self
    }

    pub fn with_response(mut self, status_code: u16, response_body: String, duration_ms: u64) -> Self {
        self.status_code = Some(status_code);
        self.response_body = Some(response_body);
        self.duration_ms = Some(duration_ms);
        self
    }
}

/// Type of log entry in the execution flow
#[derive(Debug, Clone, PartialEq)]
pub enum LogEntryType {
    UserPrompt,
    Planning,
    Discovery,
    ExecutionStart,
    RequestExec,
    RequestResult,
}

impl fmt::Display for LogEntryType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            LogEntryType::UserPrompt => write!(f, "user_prompt"),
            LogEntryType::Planning => write!(f, "planning"),
            LogEntryType::Discovery => write!(f, "discovery"),
            LogEntryType::ExecutionStart => write!(f, "execution_start"),
            LogEntryType::RequestExec => write!(f, "request_exec"),
            LogEntryType::RequestResult => write!(f, "request_result"),
        }
    }
}

/// Represents a single entry in the execution log
#[derive(Debug, Clone, PartialEq)]
pub struct LogEntry {
    pub entry_type: LogEntryType,
    pub content: String,
    pub request_number: Option<usize>,
}

impl LogEntry {
    pub fn new(entry_type: LogEntryType, content: String) -> Self {
        Self {
            entry_type,
            content,
            request_number: None,
        }
    }

    pub fn with_request_number(mut self, request_number: usize) -> Self {
        self.request_number = Some(request_number);
        self
    }
}
