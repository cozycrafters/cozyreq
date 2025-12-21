use ratatui::{
    Frame,
    crossterm::event::{KeyCode, KeyEvent},
    layout::Rect,
    widgets::Paragraph,
};

use crate::tui::components::Component;

#[derive(Default)]
pub(crate) struct Counter {
    state: u32,
}

impl Counter {
    fn increment(&mut self) {
        self.state += 1;
    }

    fn decrement(&mut self) {
        if self.state > 0 {
            self.state -= 1;
        }
    }
}

impl Component for Counter {
    fn on_key_pressed(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Up | KeyCode::Char('j') => self.increment(),
            KeyCode::Down | KeyCode::Char('k') => self.decrement(),
            _ => {}
        }
    }

    fn render(&mut self, frame: &mut Frame, area: Rect) {
        frame.render_widget(Paragraph::new(format!("Counter: {}", self.state)), area);
    }
}
