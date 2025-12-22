use ratatui::{crossterm::event::KeyEvent, widgets::WidgetRef};

pub(crate) mod counter;

pub(crate) trait Component: WidgetRef {
    fn on_key_pressed(&mut self, key: KeyEvent);
}
