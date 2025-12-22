use ratatui::{crossterm::event::KeyEvent, widgets::WidgetRef};

pub(crate) mod prompt;

pub(crate) trait Component: WidgetRef {
    fn on_key_pressed(&mut self, key: KeyEvent);
}
