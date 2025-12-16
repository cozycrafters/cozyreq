use crate::types::{AgentError, ContentBlock, Message, Tool};
use serde::{Deserialize, Serialize};

const CLAUDE_API_URL: &str = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION: &str = "2023-06-01";

/// Internal API types for Claude API wire format

#[derive(Debug, Serialize)]
struct ApiRequest {
    model: String,
    max_tokens: u32,
    system: String,
    tools: Vec<ApiTool>,
    messages: Vec<ApiMessage>,
}

#[derive(Debug, Serialize)]
struct ApiTool {
    name: String,
    description: String,
    input_schema: serde_json::Value,
}

#[derive(Debug, Serialize)]
struct ApiMessage {
    role: String,
    content: serde_json::Value,
}

#[derive(Debug, Deserialize)]
struct ApiResponse {
    content: Vec<ApiContentBlock>,
    stop_reason: String,
    usage: Usage,
}

#[derive(Debug, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
enum ApiContentBlock {
    Text {
        text: String,
    },
    ToolUse {
        id: String,
        name: String,
        input: serde_json::Value,
    },
}

#[derive(Debug, Deserialize)]
struct Usage {
    input_tokens: u32,
    output_tokens: u32,
}

/// Convert our Message types to Claude API format
fn messages_to_api_format(messages: &[Message]) -> Vec<ApiMessage> {
    let mut api_messages = Vec::new();

    for message in messages {
        match message {
            Message::User { content } => {
                api_messages.push(ApiMessage {
                    role: "user".to_string(),
                    content: serde_json::json!(content),
                });
            }
            Message::Assistant { content } => {
                let content_blocks: Vec<serde_json::Value> = content
                    .iter()
                    .map(|block| match block {
                        ContentBlock::Text { text } => {
                            serde_json::json!({
                                "type": "text",
                                "text": text
                            })
                        }
                        ContentBlock::ToolUse { id, name, input } => {
                            serde_json::json!({
                                "type": "tool_use",
                                "id": id,
                                "name": name,
                                "input": input
                            })
                        }
                    })
                    .collect();

                api_messages.push(ApiMessage {
                    role: "assistant".to_string(),
                    content: serde_json::json!(content_blocks),
                });
            }
            Message::ToolResult {
                tool_use_id,
                content,
            } => {
                // Tool results are sent as user messages with tool_result content
                api_messages.push(ApiMessage {
                    role: "user".to_string(),
                    content: serde_json::json!([{
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": content
                    }]),
                });
            }
        }
    }

    api_messages
}

/// Call the Claude API with the given parameters
pub(crate) async fn call_claude_api(
    api_key: &str,
    model: &str,
    system_prompt: &str,
    tools: &[Tool],
    messages: &[Message],
) -> Result<(Vec<ContentBlock>, String), AgentError> {
    tracing::debug!(
        message_count = messages.len(),
        tool_count = tools.len(),
        "Calling Claude API"
    );

    let client = reqwest::Client::new();

    // Convert tools to API format
    let api_tools: Vec<ApiTool> = tools
        .iter()
        .map(|tool| ApiTool {
            name: tool.name.clone(),
            description: tool.description.clone(),
            input_schema: tool.input_schema.clone(),
        })
        .collect();

    // Convert messages to API format
    let api_messages = messages_to_api_format(messages);

    // Build request
    let request = ApiRequest {
        model: model.to_string(),
        max_tokens: 1024,
        system: system_prompt.to_string(),
        tools: api_tools,
        messages: api_messages,
    };

    // Make the API call
    let response = client
        .post(CLAUDE_API_URL)
        .header("Content-Type", "application/json")
        .header("x-api-key", api_key)
        .header("anthropic-version", ANTHROPIC_VERSION)
        .json(&request)
        .send()
        .await
        .map_err(|e| AgentError::ApiError(format!("Failed to send request: {}", e)))?;

    // Check status
    let status = response.status();
    if !status.is_success() {
        let error_text = response
            .text()
            .await
            .unwrap_or_else(|_| "Unknown error".to_string());
        return Err(AgentError::ApiError(format!(
            "API returned status {}: {}",
            status, error_text
        )));
    }

    // Parse response
    let api_response: ApiResponse = response
        .json()
        .await
        .map_err(|e| AgentError::ParseError(format!("Failed to parse response: {}", e)))?;

    tracing::debug!(
        input_tokens = api_response.usage.input_tokens,
        output_tokens = api_response.usage.output_tokens,
        stop_reason = %api_response.stop_reason,
        "Received API response"
    );

    // Convert API content blocks to our format
    let content_blocks: Vec<ContentBlock> = api_response
        .content
        .into_iter()
        .map(|block| match block {
            ApiContentBlock::Text { text } => ContentBlock::Text { text },
            ApiContentBlock::ToolUse { id, name, input } => {
                ContentBlock::ToolUse { id, name, input }
            }
        })
        .collect();

    Ok((content_blocks, api_response.stop_reason))
}
