use crate::types::{Tool, ToolFn};
use serde_json::json;
use std::collections::HashMap;

/// Create dummy tools for testing and demonstration
pub fn create_dummy_tools() -> (Vec<Tool>, HashMap<String, ToolFn>) {
    let mut tools = Vec::new();
    let mut implementations: HashMap<String, ToolFn> = HashMap::new();

    // Tool 1: get_weather
    tools.push(Tool {
        name: "get_weather".to_string(),
        description: "Get the current weather in a given location".to_string(),
        input_schema: json!({
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The unit of temperature, either 'celsius' or 'fahrenheit'"
                }
            },
            "required": ["location"]
        }),
    });

    implementations.insert(
        "get_weather".to_string(),
        Box::new(|input: serde_json::Value| {
            let location = input["location"]
                .as_str()
                .ok_or("Missing location parameter")?;
            let unit = input["unit"].as_str().unwrap_or("celsius");
            Ok(format!(
                "Weather in {}: 15 degrees {}, sunny",
                location, unit
            ))
        }) as ToolFn,
    );

    // Tool 2: get_time
    tools.push(Tool {
        name: "get_time".to_string(),
        description: "Get the current time in a given time zone".to_string(),
        input_schema: json!({
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "The IANA time zone name, e.g. America/Los_Angeles"
                }
            },
            "required": ["timezone"]
        }),
    });

    implementations.insert(
        "get_time".to_string(),
        Box::new(|input: serde_json::Value| {
            let timezone = input["timezone"]
                .as_str()
                .ok_or("Missing timezone parameter")?;
            Ok(format!("Current time in {}: 14:30", timezone))
        }) as ToolFn,
    );

    // Tool 3: calculate
    tools.push(Tool {
        name: "calculate".to_string(),
        description: "Calculate the result of a mathematical expression".to_string(),
        input_schema: json!({
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate, e.g. '2 + 2'"
                }
            },
            "required": ["expression"]
        }),
    });

    implementations.insert(
        "calculate".to_string(),
        Box::new(|input: serde_json::Value| {
            let expression = input["expression"]
                .as_str()
                .ok_or("Missing expression parameter")?;
            // Always return 42 regardless of input (dummy implementation)
            Ok(format!("Result of '{}': 42", expression))
        }) as ToolFn,
    );

    (tools, implementations)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_dummy_tools() {
        let (tools, implementations) = create_dummy_tools();

        assert_eq!(tools.len(), 3);
        assert_eq!(implementations.len(), 3);

        assert!(tools.iter().any(|t| t.name == "get_weather"));
        assert!(tools.iter().any(|t| t.name == "get_time"));
        assert!(tools.iter().any(|t| t.name == "calculate"));
    }

    #[test]
    fn test_get_weather_tool() {
        let (_, implementations) = create_dummy_tools();
        let tool_fn = implementations.get("get_weather").unwrap();

        let input = json!({
            "location": "San Francisco, CA",
            "unit": "celsius"
        });

        let result = tool_fn(input).unwrap();
        assert_eq!(
            result,
            "Weather in San Francisco, CA: 15 degrees celsius, sunny"
        );
    }

    #[test]
    fn test_get_weather_tool_default_unit() {
        let (_, implementations) = create_dummy_tools();
        let tool_fn = implementations.get("get_weather").unwrap();

        let input = json!({
            "location": "New York, NY"
        });

        let result = tool_fn(input).unwrap();
        assert_eq!(result, "Weather in New York, NY: 15 degrees celsius, sunny");
    }

    #[test]
    fn test_get_time_tool() {
        let (_, implementations) = create_dummy_tools();
        let tool_fn = implementations.get("get_time").unwrap();

        let input = json!({
            "timezone": "America/Los_Angeles"
        });

        let result = tool_fn(input).unwrap();
        assert_eq!(result, "Current time in America/Los_Angeles: 14:30");
    }

    #[test]
    fn test_calculate_tool() {
        let (_, implementations) = create_dummy_tools();
        let tool_fn = implementations.get("calculate").unwrap();

        let input = json!({
            "expression": "2 + 2"
        });

        let result = tool_fn(input).unwrap();
        assert_eq!(result, "Result of '2 + 2': 42");
    }

    #[test]
    fn test_missing_parameter() {
        let (_, implementations) = create_dummy_tools();
        let tool_fn = implementations.get("get_weather").unwrap();

        let input = json!({});

        let result = tool_fn(input);
        assert!(result.is_err());
        assert_eq!(result.unwrap_err(), "Missing location parameter");
    }
}
