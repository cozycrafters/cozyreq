mod events;
mod model;
mod view;

use color_eyre::Result;
use crossterm::{
    execute,
    terminal::{EnterAlternateScreen, LeaveAlternateScreen, disable_raw_mode, enable_raw_mode},
};
use ratatui::{Terminal, backend::CrosstermBackend};
use std::{io, panic};

use crate::events::handle_event;
use crate::model::{RunningState, create_dummy_model, update};
use crate::view::view;

pub fn run() -> Result<()> {
    // Install panic hook
    let original_hook = panic::take_hook();
    panic::set_hook(Box::new(move |panic_info| {
        execute!(io::stdout(), LeaveAlternateScreen).unwrap();
        disable_raw_mode().unwrap();
        original_hook(panic_info);
    }));

    // Setup terminal
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // Create app with dummy data
    let mut model = create_dummy_model();

    // Main loop
    loop {
        // Render the current view
        terminal.draw(|f| view(&model, f))?;

        // Handle events and map to a Message
        let mut current_msg = handle_event(&model)?;

        // Process updates as long as they return a non-None message
        while current_msg.is_some() {
            current_msg = update(&mut model, current_msg.unwrap());
        }

        // Check if we should quit
        if model.running_state == RunningState::Done {
            break;
        }
    }

    // Restore terminal
    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;
    disable_raw_mode()?;
    Ok(())
}
