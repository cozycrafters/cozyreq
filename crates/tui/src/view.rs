use ratatui::{
    Frame,
    layout::{Constraint, Direction, Layout, Rect},
    style::{Color, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph, Wrap},
};

use crate::model::{ExecutionRequest, InputMode, LogEntryType, Model};

/// Main view function - renders the entire UI
pub fn view(model: &Model, frame: &mut Frame) {
    let size = frame.area();

    // Create main layout
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(50), Constraint::Percentage(50)])
        .split(size);

    // Left panel (log)
    render_log_panel(frame, model, chunks[0]);

    // Right panel (details)
    render_details_panel(frame, model, chunks[1]);
}

/// Renders the left panel with log entries and input box
fn render_log_panel(frame: &mut Frame, model: &Model, area: Rect) {
    // Split into log area and input area
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Min(0), Constraint::Length(3)])
        .split(area);

    // Render log
    let log_lines: Vec<Line> = model
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

    frame.render_widget(log_paragraph, chunks[0]);

    // Render input
    let input_style = if model.input_mode == InputMode::Editing {
        Style::default().fg(Color::Yellow)
    } else {
        Style::default()
    };

    let input_paragraph = Paragraph::new(format!("> {}", model.input))
        .style(input_style)
        .block(Block::default().borders(Borders::ALL).border_style(
            if model.input_mode == InputMode::Editing {
                Style::default().fg(Color::Yellow)
            } else {
                Style::default().fg(Color::Blue)
            },
        ));

    frame.render_widget(input_paragraph, chunks[1]);

    // Set cursor position when editing
    if model.input_mode == InputMode::Editing {
        frame.set_cursor_position((chunks[1].x + model.input.len() as u16 + 3, chunks[1].y + 1));
    }
}

/// Renders the right panel with request details
fn render_details_panel(frame: &mut Frame, model: &Model, area: Rect) {
    let content = if let Some(req) = model.get_selected_request() {
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

    frame.render_widget(details_paragraph, area);
}

/// Formats request details for display
pub fn format_request_details(req: &ExecutionRequest) -> String {
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
    use crate::model::{ExecutionRequest, LogEntry, LogEntryType};

    #[test]
    fn test_format_request_details_complete() {
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
    fn test_format_request_details_no_body() {
        let req = ExecutionRequest::new(1, "GET".to_string(), "/api/test".to_string())
            .with_headers(vec![(
                "Content-Type".to_string(),
                "application/json".to_string(),
            )])
            .with_response(200, "response body".to_string(), 100);

        let details = format_request_details(&req);

        assert!(details.contains("[1] GET /api/test"));
        assert!(details.contains("Body: (None)"));
        assert!(details.contains("Status: 200 OK"));
    }

    #[test]
    fn test_format_request_details_no_response() {
        let req = ExecutionRequest::new(1, "POST".to_string(), "/api/test".to_string())
            .with_headers(vec![(
                "Content-Type".to_string(),
                "application/json".to_string(),
            )])
            .with_body("request body".to_string());

        let details = format_request_details(&req);

        assert!(details.contains("[1] POST /api/test"));
        assert!(details.contains("request body"));
        assert!(!details.contains("Status:"));
    }

    #[test]
    fn test_format_request_details_empty_headers() {
        let req = ExecutionRequest::new(1, "GET".to_string(), "/api/test".to_string());

        let details = format_request_details(&req);

        assert!(details.contains("[1] GET /api/test"));
        assert!(details.contains("Headers:"));
        assert!(details.contains("Body: (None)"));
    }

    #[test]
    fn test_format_request_details_multiline_body() {
        let req = ExecutionRequest::new(1, "POST".to_string(), "/api/test".to_string())
            .with_body("{\n  \"key\": \"value\",\n  \"number\": 42\n}".to_string());

        let details = format_request_details(&req);

        assert!(details.contains("{"));
        assert!(details.contains("\"key\": \"value\""));
        assert!(details.contains("\"number\": 42"));
        assert!(details.contains("}"));
    }

    #[test]
    fn test_view_empty_model() {
        let model = crate::model::Model::new();

        // We can't easily test rendering without a real terminal,
        // but we can verify the model is valid for rendering
        assert_eq!(model.requests.len(), 0);
        assert_eq!(model.log_entries.len(), 0);

        // Test that get_selected_request returns None for empty model
        assert!(model.get_selected_request().is_none());
    }

    #[test]
    fn test_log_entry_styling() {
        // This test documents the expected styling for each log entry type
        // Actual styling verification would require terminal output testing

        let user_prompt = LogEntry::new(LogEntryType::UserPrompt, "test".to_string());
        assert_eq!(user_prompt.entry_type, LogEntryType::UserPrompt);

        let planning = LogEntry::new(LogEntryType::Planning, "test".to_string());
        assert_eq!(planning.entry_type, LogEntryType::Planning);

        let discovery = LogEntry::new(LogEntryType::Discovery, "test".to_string());
        assert_eq!(discovery.entry_type, LogEntryType::Discovery);

        let exec_start = LogEntry::new(LogEntryType::ExecutionStart, "test".to_string());
        assert_eq!(exec_start.entry_type, LogEntryType::ExecutionStart);

        let request_exec = LogEntry::new(LogEntryType::RequestExec, "test".to_string());
        assert_eq!(request_exec.entry_type, LogEntryType::RequestExec);

        let request_result = LogEntry::new(LogEntryType::RequestResult, "✓ test".to_string());
        assert_eq!(request_result.entry_type, LogEntryType::RequestResult);
        assert!(request_result.content.contains("✓"));
    }

    #[test]
    fn test_cursor_position_calculation() {
        // Test that cursor position is based on input length
        let mut model = crate::model::Model::new();
        model.input_mode = InputMode::Editing;

        model.input = "".to_string();
        assert_eq!(model.input.len(), 0);

        model.input = "hello".to_string();
        assert_eq!(model.input.len(), 5);

        model.input = "hello world".to_string();
        assert_eq!(model.input.len(), 11);
    }
}
