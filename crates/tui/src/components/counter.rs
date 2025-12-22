use ratatui::{
    buffer::Buffer,
    crossterm::event::{KeyCode, KeyEvent},
    layout::Rect,
    widgets::{Paragraph, Widget, WidgetRef},
};

use crate::components::Component;

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
}

impl WidgetRef for Counter {
    fn render_ref(&self, area: Rect, buf: &mut Buffer) {
        Paragraph::new(format!("Counter: {}", self.state)).render(area, buf);
    }
}
