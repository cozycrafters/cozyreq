async def run_agent(prompt: str) -> str:
    """Run a Pydantic AI agent with Huggingface provider."""
    from pydantic_ai import Agent

    # Create agent with Huggingface model
    agent = Agent(
        model="mistral:devstral-medium-latest",
        system_prompt="You are Kimi, an AI assistant created by Moonshot AI.",
    )

    # Run the agent with the prompt
    result = await agent.run(prompt)

    return str(result.output)
