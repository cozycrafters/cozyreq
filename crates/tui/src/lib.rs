mod events;
mod model;
mod view;

use color_eyre::Result;
use crossterm::{
    execute,
    terminal::{EnterAlternateScreen, LeaveAlternateScreen, disable_raw_mode, enable_raw_mode},
};
use ratatui::{Terminal, backend::CrosstermBackend};
use std::io;

use crate::events::handle_event;
use crate::model::{Model, RunningState, create_dummy_model, update};
use crate::view::view;

pub fn run() -> Result<()> {
    // Setup terminal
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // Create app with dummy data
    let mut model = create_dummy_model();

    // Main loop
    let res = run_app(&mut terminal, &mut model);

    // Restore terminal
    disable_raw_mode()?;
    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;
    terminal.show_cursor()?;

    if let Err(err) = res {
        eprintln!("Error: {:?}", err);
    }

    Ok(())
}

fn run_app<B: ratatui::backend::Backend>(
    terminal: &mut Terminal<B>,
    model: &mut Model,
) -> Result<()> {
    loop {
        // Render the current view
        terminal.draw(|f| view(model, f))?;

        // Handle events and map to a Message
        let mut current_msg = handle_event(model)?;

        // Process updates as long as they return a non-None message
        while current_msg.is_some() {
            current_msg = update(model, current_msg.unwrap());
        }

        // Check if we should quit
        if model.running_state == RunningState::Done {
            break;
        }
    }
    Ok(())
}
