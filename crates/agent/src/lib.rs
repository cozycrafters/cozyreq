mod claude;
mod tools;
mod types;

pub use tools::create_dummy_tools;
pub use types::{AgentError, ContentBlock, Message, Tool, ToolFn};

use std::collections::HashMap;
use tokio_util::sync::CancellationToken;

/// An AI agent that uses Claude Sonnet 4.5 to execute tool calls
pub struct Agent {
    api_key: String,
    model: String,
    system_prompt: String,
    tools: Vec<Tool>,
    tool_implementations: HashMap<String, ToolFn>,
}

impl Agent {
    /// Create a new agent with the given system prompt, tools, and implementations
    ///
    /// Reads the API key from the `ANTHROPIC_API_KEY` environment variable.
    pub fn new(
        system_prompt: String,
        tools: Vec<Tool>,
        tool_implementations: HashMap<String, ToolFn>,
    ) -> Result<Self, AgentError> {
        tracing::info!("Initializing Agent");

        let api_key = std::env::var("ANTHROPIC_API_KEY").map_err(|_| {
            AgentError::ApiError("ANTHROPIC_API_KEY environment variable not set".to_string())
        })?;

        tracing::debug!(tool_count = tools.len(), "Agent initialized with tools");

        Ok(Self {
            api_key,
            model: "claude-sonnet-4-5".to_string(),
            system_prompt,
            tools,
            tool_implementations,
        })
    }

    /// Run the agent with the given user prompt
    ///
    /// This method will loop, calling Claude API and executing tools until
    /// Claude returns a stop_reason of "end_turn" or the cancellation token is triggered.
    ///
    /// Returns the complete message history, which includes:
    /// - User messages
    /// - Assistant messages (with text and tool use)
    /// - Tool result messages
    pub async fn run(
        &self,
        prompt: String,
        cancel_token: CancellationToken,
    ) -> Result<Vec<Message>, AgentError> {
        tracing::info!(prompt = %prompt, "Agent run started");

        let mut message_history = vec![Message::User {
            content: prompt.clone(),
        }];

        let mut iteration_count = 0;

        loop {
            // Check for cancellation
            if cancel_token.is_cancelled() {
                tracing::info!("Agent execution cancelled");
                return Err(AgentError::Cancelled);
            }

            iteration_count += 1;
            tracing::debug!(iteration = iteration_count, "Starting agent iteration");

            // Call Claude API
            let (content_blocks, stop_reason) = claude::call_claude_api(
                &self.api_key,
                &self.model,
                &self.system_prompt,
                &self.tools,
                &message_history,
            )
            .await?;

            // Add assistant response to history
            let assistant_message = Message::Assistant {
                content: content_blocks.clone(),
            };
            message_history.push(assistant_message);

            tracing::debug!(
                stop_reason = %stop_reason,
                content_block_count = content_blocks.len(),
                "Received assistant response"
            );

            // Check stop reason
            if stop_reason == "end_turn" {
                tracing::info!(
                    total_messages = message_history.len(),
                    iterations = iteration_count,
                    "Agent run completed"
                );
                break;
            }

            // If stop_reason is "tool_use", extract and execute tool calls
            if stop_reason == "tool_use" {
                let tool_uses: Vec<_> = content_blocks
                    .iter()
                    .filter_map(|block| match block {
                        ContentBlock::ToolUse { id, name, input } => {
                            Some((id.clone(), name.clone(), input.clone()))
                        }
                        _ => None,
                    })
                    .collect();

                tracing::debug!(tool_call_count = tool_uses.len(), "Executing tool calls");

                // Execute each tool
                for (tool_use_id, tool_name, tool_input) in tool_uses {
                    tracing::info!(
                        tool_name = %tool_name,
                        tool_input = ?tool_input,
                        "Executing tool"
                    );

                    // Look up tool implementation
                    let tool_fn = self
                        .tool_implementations
                        .get(&tool_name)
                        .ok_or_else(|| AgentError::ToolNotFound(tool_name.clone()))?;

                    // Execute tool and handle errors
                    let result_content = match tool_fn(tool_input) {
                        Ok(output) => {
                            tracing::debug!(
                                tool_name = %tool_name,
                                output_length = output.len(),
                                "Tool execution succeeded"
                            );
                            output
                        }
                        Err(error_msg) => {
                            tracing::warn!(
                                tool_name = %tool_name,
                                error = %error_msg,
                                "Tool execution failed"
                            );
                            format!("Error: {}", error_msg)
                        }
                    };

                    // Add tool result to message history
                    message_history.push(Message::ToolResult {
                        tool_use_id,
                        content: result_content,
                    });
                }

                // Continue loop to get Claude's response to the tool results
                continue;
            }

            // If we get here, stop_reason is neither "end_turn" nor "tool_use"
            tracing::warn!(
                stop_reason = %stop_reason,
                "Unexpected stop_reason, treating as completion"
            );
            break;
        }

        Ok(message_history)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_agent_creation_with_api_key() {
        // Save current value
        let original = std::env::var("ANTHROPIC_API_KEY").ok();

        unsafe {
            std::env::set_var("ANTHROPIC_API_KEY", "test-key");
        }

        let (tools, implementations) = create_dummy_tools();
        let result = Agent::new("Test prompt".to_string(), tools, implementations);

        // Restore original value
        unsafe {
            if let Some(val) = original {
                std::env::set_var("ANTHROPIC_API_KEY", val);
            } else {
                std::env::remove_var("ANTHROPIC_API_KEY");
            }
        }

        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_cancellation() {
        // Save current value
        let original = std::env::var("ANTHROPIC_API_KEY").ok();

        unsafe {
            std::env::set_var("ANTHROPIC_API_KEY", "test-key");
        }

        let (tools, implementations) = create_dummy_tools();
        let agent = Agent::new("Test prompt".to_string(), tools, implementations).unwrap();

        let cancel_token = CancellationToken::new();
        cancel_token.cancel(); // Cancel immediately

        let result = agent.run("Hello".to_string(), cancel_token).await;

        // Restore original value
        unsafe {
            if let Some(val) = original {
                std::env::set_var("ANTHROPIC_API_KEY", val);
            } else {
                std::env::remove_var("ANTHROPIC_API_KEY");
            }
        }

        assert!(result.is_err());
        match result {
            Err(AgentError::Cancelled) => (),
            _ => panic!("Expected Cancelled error"),
        }
    }
}
