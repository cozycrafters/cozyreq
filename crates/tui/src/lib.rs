use std::{io, panic, time::Duration};

use ratatui::{
    Terminal,
    buffer::Buffer,
    crossterm::{
        ExecutableCommand,
        event::{self, Event, KeyCode, KeyEvent},
        terminal::{EnterAlternateScreen, LeaveAlternateScreen, disable_raw_mode, enable_raw_mode},
    },
    layout::Rect,
    prelude::{Backend, CrosstermBackend},
    widgets::WidgetRef,
};

use crate::components::{Component, counter::Counter};

mod components;

#[derive(Default)]
pub struct App {
    components: Vec<Box<dyn Component>>,
    should_stop: bool,
}

impl App {
    pub fn new() -> Self {
        Self {
            components: vec![Box::new(Counter::default())],
            should_stop: false,
        }
    }

    pub async fn run(&mut self) -> color_eyre::Result<()> {
        install_panic_hook();
        let mut terminal = init_terminal()?;
        let mut app = App::new();
        loop {
            terminal.draw(|f| f.render_widget(&app, f.area()))?;
            app.handle_events()?;
            if app.should_stop {
                break;
            }
        }
        restore_terminal()?;
        Ok(())
    }

    fn handle_events(&mut self) -> color_eyre::Result<()> {
        if event::poll(Duration::from_millis(250))?
            && let Event::Key(key) = event::read()?
            && key.kind == event::KeyEventKind::Press
        {
            {
                self.on_key_pressed(key);
            }
        }
        Ok(())
    }

    pub fn on_key_pressed(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Char('q') => self.should_stop = true,
            _ => {
                for component in &mut self.components {
                    component.on_key_pressed(key);
                }
            }
        }
    }
}

impl WidgetRef for App {
    fn render_ref(&self, area: Rect, buf: &mut Buffer) {
        for component in &self.components {
            component.render_ref(area, buf);
        }
    }
}

fn init_terminal() -> color_eyre::Result<Terminal<impl Backend>> {
    enable_raw_mode()?;
    io::stdout().execute(EnterAlternateScreen)?;
    let terminal = Terminal::new(CrosstermBackend::new(io::stdout()))?;
    Ok(terminal)
}

fn restore_terminal() -> color_eyre::Result<()> {
    io::stdout().execute(LeaveAlternateScreen)?;
    disable_raw_mode()?;
    Ok(())
}

fn install_panic_hook() {
    let original_hook = panic::take_hook();
    panic::set_hook(Box::new(move |panic_info| {
        io::stdout().execute(LeaveAlternateScreen).unwrap();
        disable_raw_mode().unwrap();
        original_hook(panic_info);
    }));
}
