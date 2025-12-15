use std::fmt;

use crate::events::Message;

/// Represents a single HTTP request in the execution flow
#[derive(Debug, Clone, PartialEq)]
pub(crate) struct ExecutionRequest {
    pub(crate) number: usize,
    pub(crate) method: String,
    pub(crate) url: String,
    pub(crate) headers: Vec<(String, String)>,
    pub(crate) body: Option<String>,
    pub(crate) status_code: Option<u16>,
    pub(crate) response_body: Option<String>,
    duration_ms: Option<u64>,
}

impl ExecutionRequest {
    pub(crate) fn new(number: usize, method: String, url: String) -> Self {
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

    pub(crate) fn with_headers(mut self, headers: Vec<(String, String)>) -> Self {
        self.headers = headers;
        self
    }

    pub(crate) fn with_body(mut self, body: String) -> Self {
        self.body = Some(body);
        self
    }

    pub(crate) fn with_response(
        mut self,
        status_code: u16,
        response_body: String,
        duration_ms: u64,
    ) -> Self {
        self.status_code = Some(status_code);
        self.response_body = Some(response_body);
        self.duration_ms = Some(duration_ms);
        self
    }
}

/// Type of log entry in the execution flow
#[derive(Debug, Clone, PartialEq)]
pub(crate) enum LogEntryType {
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
pub(crate) struct LogEntry {
    pub(crate) entry_type: LogEntryType,
    pub(crate) content: String,
    request_number: Option<usize>,
}

impl LogEntry {
    pub(crate) fn new(entry_type: LogEntryType, content: String) -> Self {
        Self {
            entry_type,
            content,
            request_number: None,
        }
    }

    fn with_request_number(mut self, request_number: usize) -> Self {
        self.request_number = Some(request_number);
        self
    }
}

/// Input mode for the application
#[derive(Debug, PartialEq, Clone)]
pub(crate) enum InputMode {
    Normal,
    Editing,
}

/// Running state of the application
#[derive(Debug, PartialEq, Clone)]
pub(crate) enum RunningState {
    Running,
    Done,
}

/// The main TUI application state
#[derive(Debug)]
pub(crate) struct Model {
    pub(crate) requests: Vec<ExecutionRequest>,
    pub(crate) log_entries: Vec<LogEntry>,
    selected_request_index: usize,
    pub(crate) input: String,
    pub(crate) input_mode: InputMode,
    pub(crate) running_state: RunningState,
}

impl Model {
    pub(crate) fn new() -> Self {
        Self {
            requests: Vec::new(),
            log_entries: Vec::new(),
            selected_request_index: 0,
            input: String::new(),
            input_mode: InputMode::Normal,
            running_state: RunningState::Running,
        }
    }

    pub(crate) fn get_selected_request(&self) -> Option<&ExecutionRequest> {
        self.requests.get(self.selected_request_index)
    }
}

impl Default for Model {
    fn default() -> Self {
        Self::new()
    }
}

/// Updates the model based on a message
///
/// Returns an optional message for chaining (Finite State Machine pattern)
pub(crate) fn update(model: &mut Model, msg: Message) -> Option<Message> {
    match msg {
        Message::NavigateUp => {
            if model.selected_request_index > 0 {
                model.selected_request_index -= 1;
            }
        }
        Message::NavigateDown => {
            if !model.requests.is_empty() && model.selected_request_index < model.requests.len() - 1
            {
                model.selected_request_index += 1;
            }
        }
        Message::EnterEditMode => {
            model.input_mode = InputMode::Editing;
        }
        Message::ExitEditMode => {
            model.input_mode = InputMode::Normal;
        }
        Message::InputChar(c) => {
            model.input.push(c);
        }
        Message::DeleteChar => {
            model.input.pop();
        }
        Message::SubmitPrompt => {
            let message = model.input.trim().to_string();
            if !message.is_empty() {
                submit_prompt(model, message);
            }
            model.input.clear();
            model.input_mode = InputMode::Normal;
        }
        Message::Quit => {
            model.running_state = RunningState::Done;
        }
    }
    None
}

/// Helper function to add a user prompt to the log
fn submit_prompt(model: &mut Model, message: String) {
    // Add blank line
    model
        .log_entries
        .push(LogEntry::new(LogEntryType::UserPrompt, "".to_string()));
    // Add user prompt
    model.log_entries.push(LogEntry::new(
        LogEntryType::UserPrompt,
        format!("> {}", message),
    ));
    // Add planning status
    model
        .log_entries
        .push(LogEntry::new(LogEntryType::UserPrompt, "".to_string()));
    model.log_entries.push(LogEntry::new(
        LogEntryType::Planning,
        "🤖 Planning...".to_string(),
    ));
}

/// Helper to create a model with dummy data for testing and development
pub fn create_dummy_model() -> Model {
    let mut model = Model::new();

    // Add dummy log entries
    model.log_entries.push(LogEntry::new(
        LogEntryType::UserPrompt,
        "> get all users and update first email".to_string(),
    ));
    model
        .log_entries
        .push(LogEntry::new(LogEntryType::UserPrompt, "".to_string()));
    model.log_entries.push(LogEntry::new(
        LogEntryType::Planning,
        "🤖 Planning...".to_string(),
    ));
    model.log_entries.push(LogEntry::new(
        LogEntryType::Discovery,
        "✓ Found: GET /api/users".to_string(),
    ));
    model.log_entries.push(LogEntry::new(
        LogEntryType::Discovery,
        "✓ Found: POST /api/users".to_string(),
    ));
    model
        .log_entries
        .push(LogEntry::new(LogEntryType::UserPrompt, "".to_string()));
    model.log_entries.push(LogEntry::new(
        LogEntryType::ExecutionStart,
        "🔄 Executing:".to_string(),
    ));
    model.log_entries.push(
        LogEntry::new(LogEntryType::RequestExec, "[1] GET /api/users".to_string())
            .with_request_number(1),
    );
    model.log_entries.push(
        LogEntry::new(
            LogEntryType::RequestResult,
            "    ✓ 200 OK (145ms)".to_string(),
        )
        .with_request_number(1),
    );
    model.log_entries.push(
        LogEntry::new(
            LogEntryType::RequestExec,
            "[2] POST /api/users/1".to_string(),
        )
        .with_request_number(2),
    );
    model.log_entries.push(
        LogEntry::new(
            LogEntryType::RequestResult,
            "    ✓ 200 OK (89ms)".to_string(),
        )
        .with_request_number(2),
    );

    // Add dummy requests
    model.requests.push(
        ExecutionRequest::new(1, "GET".to_string(), "/api/users".to_string())
            .with_headers(vec![(
                "Content-Type".to_string(),
                "application/json".to_string(),
            )])
            .with_response(
                200,
                r#"[{"id": 1, "email": "old@example.com"}, ...]"#.to_string(),
                145,
            ),
    );
    model.requests.push(
        ExecutionRequest::new(2, "POST".to_string(), "/api/users/1".to_string())
            .with_headers(vec![(
                "Content-Type".to_string(),
                "application/json".to_string(),
            )])
            .with_body("{\n  \"email\": \"new@example.com\"\n}".to_string())
            .with_response(
                200,
                "{\n  \"id\": 1,\n  \"email\": \"new@example.com\"\n}".to_string(),
                89,
            ),
    );

    model.selected_request_index = 1;
    model
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_model_new() {
        let model = Model::new();
        assert_eq!(model.requests.len(), 0);
        assert_eq!(model.log_entries.len(), 0);
        assert_eq!(model.selected_request_index, 0);
        assert_eq!(model.input, "");
        assert_eq!(model.input_mode, InputMode::Normal);
        assert_eq!(model.running_state, RunningState::Running);
    }

    #[test]
    fn test_get_selected_request() {
        let model = create_dummy_model();
        let selected = model.get_selected_request();
        assert!(selected.is_some());
        assert_eq!(selected.unwrap().number, 2);
    }

    #[test]
    fn test_get_selected_request_none() {
        let mut model = Model::new();
        assert!(model.get_selected_request().is_none());

        model.selected_request_index = 10;
        assert!(model.get_selected_request().is_none());
    }

    #[test]
    fn test_execution_request_builder() {
        let req = ExecutionRequest::new(1, "GET".to_string(), "/api/test".to_string())
            .with_headers(vec![(
                "Content-Type".to_string(),
                "application/json".to_string(),
            )])
            .with_body("test body".to_string())
            .with_response(200, "response body".to_string(), 100);

        assert_eq!(req.number, 1);
        assert_eq!(req.method, "GET");
        assert_eq!(req.url, "/api/test");
        assert_eq!(req.headers.len(), 1);
        assert_eq!(req.headers[0].0, "Content-Type");
        assert_eq!(req.body, Some("test body".to_string()));
        assert_eq!(req.status_code, Some(200));
        assert_eq!(req.response_body, Some("response body".to_string()));
        assert_eq!(req.duration_ms, Some(100));
    }

    #[test]
    fn test_log_entry_builder() {
        let entry = LogEntry::new(LogEntryType::RequestExec, "test content".to_string())
            .with_request_number(5);

        assert_eq!(entry.entry_type, LogEntryType::RequestExec);
        assert_eq!(entry.content, "test content");
        assert_eq!(entry.request_number, Some(5));
    }

    #[test]
    fn test_log_entry_type_display() {
        assert_eq!(format!("{}", LogEntryType::UserPrompt), "user_prompt");
        assert_eq!(format!("{}", LogEntryType::Planning), "planning");
        assert_eq!(format!("{}", LogEntryType::Discovery), "discovery");
        assert_eq!(
            format!("{}", LogEntryType::ExecutionStart),
            "execution_start"
        );
        assert_eq!(format!("{}", LogEntryType::RequestExec), "request_exec");
        assert_eq!(format!("{}", LogEntryType::RequestResult), "request_result");
    }

    #[test]
    fn test_create_dummy_model() {
        let model = create_dummy_model();
        assert_eq!(model.requests.len(), 2);
        assert_eq!(model.selected_request_index, 1);
        assert!(model.log_entries.len() > 0);
        assert_eq!(model.input_mode, InputMode::Normal);
        assert_eq!(model.running_state, RunningState::Running);
    }

    #[test]
    fn test_model_default() {
        let model = Model::default();
        assert_eq!(model.requests.len(), 0);
        assert_eq!(model.running_state, RunningState::Running);
    }

    #[test]
    fn test_update_navigate_up() {
        let mut model = create_dummy_model();
        assert_eq!(model.selected_request_index, 1);

        update(&mut model, Message::NavigateUp);
        assert_eq!(model.selected_request_index, 0);
    }

    #[test]
    fn test_update_navigate_down() {
        let mut model = create_dummy_model();
        model.selected_request_index = 0;

        update(&mut model, Message::NavigateDown);
        assert_eq!(model.selected_request_index, 1);
    }

    #[test]
    fn test_update_navigate_up_at_boundary() {
        let mut model = create_dummy_model();
        model.selected_request_index = 0;

        update(&mut model, Message::NavigateUp);
        assert_eq!(model.selected_request_index, 0);
    }

    #[test]
    fn test_update_navigate_down_at_boundary() {
        let mut model = create_dummy_model();
        model.selected_request_index = 1; // Last index

        update(&mut model, Message::NavigateDown);
        assert_eq!(model.selected_request_index, 1);
    }

    #[test]
    fn test_update_navigate_empty_list() {
        let mut model = Model::new();
        assert_eq!(model.requests.len(), 0);

        update(&mut model, Message::NavigateUp);
        assert_eq!(model.selected_request_index, 0);

        update(&mut model, Message::NavigateDown);
        assert_eq!(model.selected_request_index, 0);
    }

    #[test]
    fn test_update_enter_edit_mode() {
        let mut model = Model::new();
        assert_eq!(model.input_mode, InputMode::Normal);

        update(&mut model, Message::EnterEditMode);
        assert_eq!(model.input_mode, InputMode::Editing);
    }

    #[test]
    fn test_update_exit_edit_mode() {
        let mut model = Model::new();
        model.input_mode = InputMode::Editing;

        update(&mut model, Message::ExitEditMode);
        assert_eq!(model.input_mode, InputMode::Normal);
    }

    #[test]
    fn test_update_input_char() {
        let mut model = Model::new();
        assert_eq!(model.input, "");

        update(&mut model, Message::InputChar('h'));
        assert_eq!(model.input, "h");

        update(&mut model, Message::InputChar('i'));
        assert_eq!(model.input, "hi");
    }

    #[test]
    fn test_update_delete_char() {
        let mut model = Model::new();
        model.input = "hello".to_string();

        update(&mut model, Message::DeleteChar);
        assert_eq!(model.input, "hell");

        update(&mut model, Message::DeleteChar);
        assert_eq!(model.input, "hel");
    }

    #[test]
    fn test_update_delete_char_empty() {
        let mut model = Model::new();
        assert_eq!(model.input, "");

        update(&mut model, Message::DeleteChar);
        assert_eq!(model.input, "");
    }

    #[test]
    fn test_update_submit_prompt_with_text() {
        let mut model = Model::new();
        model.input = "test prompt".to_string();
        model.input_mode = InputMode::Editing;
        let initial_log_count = model.log_entries.len();

        update(&mut model, Message::SubmitPrompt);

        assert_eq!(model.input, "");
        assert_eq!(model.input_mode, InputMode::Normal);
        assert_eq!(model.log_entries.len(), initial_log_count + 4);
        assert!(
            model
                .log_entries
                .iter()
                .any(|e| e.content.contains("test prompt"))
        );
        assert!(
            model
                .log_entries
                .iter()
                .any(|e| e.content.contains("Planning"))
        );
    }

    #[test]
    fn test_update_submit_prompt_empty() {
        let mut model = Model::new();
        model.input = "   ".to_string();
        model.input_mode = InputMode::Editing;
        let initial_log_count = model.log_entries.len();

        update(&mut model, Message::SubmitPrompt);

        assert_eq!(model.input, "");
        assert_eq!(model.input_mode, InputMode::Normal);
        assert_eq!(model.log_entries.len(), initial_log_count);
    }

    #[test]
    fn test_update_quit() {
        let mut model = Model::new();
        assert_eq!(model.running_state, RunningState::Running);

        update(&mut model, Message::Quit);
        assert_eq!(model.running_state, RunningState::Done);
    }

    #[test]
    fn test_update_returns_none() {
        let mut model = Model::new();

        // Test that all message types return None (no chaining currently implemented)
        assert_eq!(update(&mut model, Message::Quit), None);
        assert_eq!(update(&mut model, Message::NavigateUp), None);
        assert_eq!(update(&mut model, Message::NavigateDown), None);
        assert_eq!(update(&mut model, Message::EnterEditMode), None);
        assert_eq!(update(&mut model, Message::ExitEditMode), None);
        assert_eq!(update(&mut model, Message::InputChar('a')), None);
        assert_eq!(update(&mut model, Message::DeleteChar), None);
        assert_eq!(update(&mut model, Message::SubmitPrompt), None);
    }
}
