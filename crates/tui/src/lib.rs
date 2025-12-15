use color_eyre::Result;
use crossterm::{
    event::{self, Event, KeyCode, KeyEvent, KeyModifiers},
    execute,
    terminal::{EnterAlternateScreen, LeaveAlternateScreen, disable_raw_mode, enable_raw_mode},
};
use ratatui::{
    Terminal,
    backend::CrosstermBackend,
    layout::{Constraint, Direction, Layout, Rect},
    style::{Color, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph, Wrap},
};
use std::fmt;
use std::io;

/// Represents a single HTTP request in the execution flow
#[derive(Debug, Clone, PartialEq)]
struct ExecutionRequest {
    number: usize,
    method: String,
    url: String,
    headers: Vec<(String, String)>,
    body: Option<String>,
    status_code: Option<u16>,
    response_body: Option<String>,
    duration_ms: Option<u64>,
}

impl ExecutionRequest {
    fn new(number: usize, method: String, url: String) -> Self {
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

    fn with_headers(mut self, headers: Vec<(String, String)>) -> Self {
        self.headers = headers;
        self
    }

    fn with_body(mut self, body: String) -> Self {
        self.body = Some(body);
        self
    }

    fn with_response(mut self, status_code: u16, response_body: String, duration_ms: u64) -> Self {
        self.status_code = Some(status_code);
        self.response_body = Some(response_body);
        self.duration_ms = Some(duration_ms);
        self
    }
}

/// Type of log entry in the execution flow
#[derive(Debug, Clone, PartialEq)]
enum LogEntryType {
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
struct LogEntry {
    pub entry_type: LogEntryType,
    pub content: String,
    pub request_number: Option<usize>,
}

impl LogEntry {
    fn new(entry_type: LogEntryType, content: String) -> Self {
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

/// The main TUI application state
struct App {
    requests: Vec<ExecutionRequest>,
    log_entries: Vec<LogEntry>,
    selected_request_index: usize,
    input: String,
    input_mode: InputMode,
    should_quit: bool,
}

#[derive(Debug, PartialEq)]
enum InputMode {
    Normal,
    Editing,
}

impl App {
    fn new() -> Self {
        Self {
            requests: Vec::new(),
            log_entries: Vec::new(),
            selected_request_index: 0,
            input: String::new(),
            input_mode: InputMode::Normal,
            should_quit: false,
        }
    }

    fn with_dummy_data(mut self) -> Self {
        // Add dummy log entries
        self.log_entries.push(LogEntry::new(
            LogEntryType::UserPrompt,
            "> get all users and update first email".to_string(),
        ));
        self.log_entries
            .push(LogEntry::new(LogEntryType::UserPrompt, "".to_string()));
        self.log_entries.push(LogEntry::new(
            LogEntryType::Planning,
            "🤖 Planning...".to_string(),
        ));
        self.log_entries.push(LogEntry::new(
            LogEntryType::Discovery,
            "✓ Found: GET /api/users".to_string(),
        ));
        self.log_entries.push(LogEntry::new(
            LogEntryType::Discovery,
            "✓ Found: POST /api/users".to_string(),
        ));
        self.log_entries
            .push(LogEntry::new(LogEntryType::UserPrompt, "".to_string()));
        self.log_entries.push(LogEntry::new(
            LogEntryType::ExecutionStart,
            "🔄 Executing:".to_string(),
        ));
        self.log_entries.push(
            LogEntry::new(LogEntryType::RequestExec, "[1] GET /api/users".to_string())
                .with_request_number(1),
        );
        self.log_entries.push(
            LogEntry::new(
                LogEntryType::RequestResult,
                "    ✓ 200 OK (145ms)".to_string(),
            )
            .with_request_number(1),
        );
        self.log_entries.push(
            LogEntry::new(
                LogEntryType::RequestExec,
                "[2] POST /api/users/1".to_string(),
            )
            .with_request_number(2),
        );
        self.log_entries.push(
            LogEntry::new(
                LogEntryType::RequestResult,
                "    ✓ 200 OK (89ms)".to_string(),
            )
            .with_request_number(2),
        );

        // Add dummy requests
        self.requests.push(
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
        self.requests.push(
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

        self.selected_request_index = 1;
        self
    }

    fn handle_key_event(&mut self, key: KeyEvent) {
        match self.input_mode {
            InputMode::Normal => self.handle_normal_mode(key),
            InputMode::Editing => self.handle_editing_mode(key),
        }
    }

    fn handle_normal_mode(&mut self, key: KeyEvent) {
        match (key.code, key.modifiers) {
            (KeyCode::Char('q'), KeyModifiers::NONE) => self.should_quit = true,
            (KeyCode::Char('i'), KeyModifiers::NONE) => self.input_mode = InputMode::Editing,
            (KeyCode::Up, KeyModifiers::NONE) => {
                if self.selected_request_index > 0 {
                    self.selected_request_index -= 1;
                }
            }
            (KeyCode::Down, KeyModifiers::NONE) => {
                if !self.requests.is_empty()
                    && self.selected_request_index < self.requests.len() - 1
                {
                    self.selected_request_index += 1;
                }
            }
            _ => {}
        }
    }

    fn handle_editing_mode(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Enter => {
                let message = self.input.trim().to_string();
                if !message.is_empty() {
                    self.submit_prompt(message);
                }
                self.input.clear();
                self.input_mode = InputMode::Normal;
            }
            KeyCode::Char(c) => {
                self.input.push(c);
            }
            KeyCode::Backspace => {
                self.input.pop();
            }
            KeyCode::Esc => {
                self.input_mode = InputMode::Normal;
            }
            _ => {}
        }
    }

    fn submit_prompt(&mut self, message: String) {
        // Add blank line
        self.log_entries
            .push(LogEntry::new(LogEntryType::UserPrompt, "".to_string()));
        // Add user prompt
        self.log_entries.push(LogEntry::new(
            LogEntryType::UserPrompt,
            format!("> {}", message),
        ));
        // Add planning status
        self.log_entries
            .push(LogEntry::new(LogEntryType::UserPrompt, "".to_string()));
        self.log_entries.push(LogEntry::new(
            LogEntryType::Planning,
            "🤖 Planning...".to_string(),
        ));
    }

    pub fn get_selected_request(&self) -> Option<&ExecutionRequest> {
        self.requests.get(self.selected_request_index)
    }
}

impl Default for App {
    fn default() -> Self {
        Self::new()
    }
}

pub fn run() -> Result<()> {
    // Setup terminal
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // Create app with dummy data
    let mut app = App::new().with_dummy_data();

    // Main loop
    let res = run_app(&mut terminal, &mut app);

    // Restore terminal
    disable_raw_mode()?;
    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;
    terminal.show_cursor()?;

    if let Err(err) = res {
        eprintln!("Error: {:?}", err);
    }

    Ok(())
}

fn run_app<B: ratatui::backend::Backend>(terminal: &mut Terminal<B>, app: &mut App) -> Result<()> {
    loop {
        terminal.draw(|f| ui(f, app))?;

        if event::poll(std::time::Duration::from_millis(100))?
            && let Event::Key(key) = event::read()?
        {
            app.handle_key_event(key);
        }

        if app.should_quit {
            break;
        }
    }
    Ok(())
}

fn ui(f: &mut ratatui::Frame, app: &App) {
    let size = f.area();

    // Create main layout
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(50), Constraint::Percentage(50)])
        .split(size);

    // Left panel (log)
    render_log_panel(f, app, chunks[0]);

    // Right panel (details)
    render_details_panel(f, app, chunks[1]);
}

fn render_log_panel(f: &mut ratatui::Frame, app: &App, area: Rect) {
    // Split into log area and input area
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Min(0), Constraint::Length(3)])
        .split(area);

    // Render log
    let log_lines: Vec<Line> = app
        .log_entries
        .iter()
        .map(|entry| {
            let style = match entry.entry_type {
                LogEntryType::UserPrompt => Style::default().fg(Color::White),
                LogEntryType::Planning => Style::default().fg(Color::Cyan),
                LogEntryType::Discovery => Style::default().fg(Color::Green),
                LogEntryType::ExecutionStart => Style::default().fg(Color::Blue),
                LogEntryType::RequestExec => Style::default().fg(Color::Blue),
                LogEntryType::RequestResult => {
                    if entry.content.contains("✓") {
                        Style::default().fg(Color::Green)
                    } else {
                        Style::default().fg(Color::Red)
                    }
                }
            };
            Line::from(Span::styled(&entry.content, style))
        })
        .collect();

    let log_paragraph = Paragraph::new(log_lines)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .border_style(Style::default().fg(Color::Blue))
                .title("CozyReq"),
        )
        .wrap(Wrap { trim: false });

    f.render_widget(log_paragraph, chunks[0]);

    // Render input
    let input_style = if app.input_mode == InputMode::Editing {
        Style::default().fg(Color::Yellow)
    } else {
        Style::default()
    };

    let input_paragraph = Paragraph::new(format!("> {}", app.input))
        .style(input_style)
        .block(Block::default().borders(Borders::ALL).border_style(
            if app.input_mode == InputMode::Editing {
                Style::default().fg(Color::Yellow)
            } else {
                Style::default().fg(Color::Blue)
            },
        ));

    f.render_widget(input_paragraph, chunks[1]);

    // Set cursor position when editing
    if app.input_mode == InputMode::Editing {
        f.set_cursor_position((chunks[1].x + app.input.len() as u16 + 3, chunks[1].y + 1));
    }
}

fn render_details_panel(f: &mut ratatui::Frame, app: &App, area: Rect) {
    let content = if let Some(req) = app.get_selected_request() {
        format_request_details(req)
    } else {
        "No request selected".to_string()
    };

    let details_paragraph = Paragraph::new(content)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .border_style(Style::default().fg(Color::Blue))
                .title("Request Details"),
        )
        .wrap(Wrap { trim: false });

    f.render_widget(details_paragraph, area);
}

fn format_request_details(req: &ExecutionRequest) -> String {
    let mut details = Vec::new();

    details.push(format!("[{}] {} {}", req.number, req.method, req.url));
    details.push(String::new());
    details.push("▼ Request".to_string());
    details.push("Headers:".to_string());
    for (key, value) in &req.headers {
        details.push(format!("  {}: {}", key, value));
    }
    if let Some(body) = &req.body {
        details.push("Body:".to_string());
        for line in body.lines() {
            details.push(line.to_string());
        }
    } else {
        details.push("Body: (None)".to_string());
    }
    details.push(String::new());
    details.push("▼ Response".to_string());
    if let Some(status_code) = req.status_code {
        details.push(format!("Status: {} OK", status_code));
    }
    if let Some(response_body) = &req.response_body {
        for line in response_body.lines() {
            details.push(line.to_string());
        }
    }

    details.join("\n")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_app_new() {
        let app = App::new();
        assert_eq!(app.requests.len(), 0);
        assert_eq!(app.log_entries.len(), 0);
        assert_eq!(app.selected_request_index, 0);
        assert_eq!(app.input, "");
        assert_eq!(app.input_mode, InputMode::Normal);
        assert_eq!(app.should_quit, false);
    }

    #[test]
    fn test_app_with_dummy_data() {
        let app = App::new().with_dummy_data();
        assert_eq!(app.requests.len(), 2);
        assert_eq!(app.selected_request_index, 1);
        assert!(app.log_entries.len() > 0);
    }

    #[test]
    fn test_handle_quit_key() {
        let mut app = App::new();
        app.handle_key_event(KeyEvent::new(KeyCode::Char('q'), KeyModifiers::NONE));
        assert!(app.should_quit);
    }

    #[test]
    fn test_handle_i_enters_edit_mode() {
        let mut app = App::new();
        app.handle_key_event(KeyEvent::new(KeyCode::Char('i'), KeyModifiers::NONE));
        assert_eq!(app.input_mode, InputMode::Editing);
    }

    #[test]
    fn test_handle_up_down_navigation() {
        let mut app = App::new().with_dummy_data();
        assert_eq!(app.selected_request_index, 1);

        app.handle_key_event(KeyEvent::new(KeyCode::Up, KeyModifiers::NONE));
        assert_eq!(app.selected_request_index, 0);

        app.handle_key_event(KeyEvent::new(KeyCode::Down, KeyModifiers::NONE));
        assert_eq!(app.selected_request_index, 1);

        // Should not go beyond bounds
        app.handle_key_event(KeyEvent::new(KeyCode::Down, KeyModifiers::NONE));
        assert_eq!(app.selected_request_index, 1);

        app.selected_request_index = 0;
        app.handle_key_event(KeyEvent::new(KeyCode::Up, KeyModifiers::NONE));
        assert_eq!(app.selected_request_index, 0);
    }

    #[test]
    fn test_input_mode_typing() {
        let mut app = App::new();
        app.input_mode = InputMode::Editing;

        app.handle_key_event(KeyEvent::new(KeyCode::Char('h'), KeyModifiers::NONE));
        app.handle_key_event(KeyEvent::new(KeyCode::Char('i'), KeyModifiers::NONE));
        assert_eq!(app.input, "hi");

        app.handle_key_event(KeyEvent::new(KeyCode::Backspace, KeyModifiers::NONE));
        assert_eq!(app.input, "h");
    }

    #[test]
    fn test_submit_prompt() {
        let mut app = App::new();
        app.input_mode = InputMode::Editing;
        app.input = "test prompt".to_string();

        app.handle_key_event(KeyEvent::new(KeyCode::Enter, KeyModifiers::NONE));

        assert_eq!(app.input, "");
        assert_eq!(app.input_mode, InputMode::Normal);
        assert!(
            app.log_entries
                .iter()
                .any(|e| e.content.contains("test prompt"))
        );
    }

    #[test]
    fn test_escape_exits_edit_mode() {
        let mut app = App::new();
        app.input_mode = InputMode::Editing;
        app.input = "some text".to_string();

        app.handle_key_event(KeyEvent::new(KeyCode::Esc, KeyModifiers::NONE));

        assert_eq!(app.input_mode, InputMode::Normal);
        // Input should still contain the text
        assert_eq!(app.input, "some text");
    }

    #[test]
    fn test_get_selected_request() {
        let app = App::new().with_dummy_data();
        let selected = app.get_selected_request();
        assert!(selected.is_some());
        assert_eq!(selected.unwrap().number, 2);
    }

    #[test]
    fn test_format_request_details() {
        let req = ExecutionRequest::new(1, "GET".to_string(), "/api/test".to_string())
            .with_headers(vec![(
                "Content-Type".to_string(),
                "application/json".to_string(),
            )])
            .with_body("test body".to_string())
            .with_response(200, "response body".to_string(), 100);

        let details = format_request_details(&req);

        assert!(details.contains("[1] GET /api/test"));
        assert!(details.contains("Content-Type: application/json"));
        assert!(details.contains("test body"));
        assert!(details.contains("Status: 200 OK"));
        assert!(details.contains("response body"));
    }

    #[test]
    fn test_empty_input_not_submitted() {
        let mut app = App::new();
        app.input_mode = InputMode::Editing;
        app.input = "   ".to_string();

        let initial_log_count = app.log_entries.len();
        app.handle_key_event(KeyEvent::new(KeyCode::Enter, KeyModifiers::NONE));

        // Should not add log entries for empty input
        assert_eq!(app.log_entries.len(), initial_log_count);
    }
}
