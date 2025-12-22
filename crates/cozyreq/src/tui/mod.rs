use std::{io, panic};

use ratatui::{
    Terminal,
    crossterm::{
        ExecutableCommand,
        terminal::{EnterAlternateScreen, LeaveAlternateScreen, disable_raw_mode, enable_raw_mode},
    },
    prelude::{Backend, CrosstermBackend},
};

use crate::tui::{
    model::{Model, RunningState},
    view::view,
};

mod event;
mod model;
mod view;

pub async fn run() -> color_eyre::Result<()> {
    install_panic_hook();
    let mut terminal = init_terminal()?;
    let mut model = Model::default();
    loop {
        terminal.draw(|f| view(&mut model, f))?;
        let mut current_msg = event::handle(&model)?;
        loop {
            match current_msg {
                Some(msg) => {
                    current_msg = model::update(&mut model, msg);
                }
                None => break,
            }
        }
        if model.running_state == RunningState::Stopped {
            break;
        }
    }
    restore_terminal()?;
    Ok(())
}

pub fn init_terminal() -> color_eyre::Result<Terminal<impl Backend>> {
    enable_raw_mode()?;
    io::stdout().execute(EnterAlternateScreen)?;
    let terminal = Terminal::new(CrosstermBackend::new(io::stdout()))?;
    Ok(terminal)
}

pub fn restore_terminal() -> color_eyre::Result<()> {
    io::stdout().execute(LeaveAlternateScreen)?;
    disable_raw_mode()?;
    Ok(())
}

pub fn install_panic_hook() {
    let original_hook = panic::take_hook();
    panic::set_hook(Box::new(move |panic_info| {
        io::stdout().execute(LeaveAlternateScreen).unwrap();
        disable_raw_mode().unwrap();
        original_hook(panic_info);
    }));
}
