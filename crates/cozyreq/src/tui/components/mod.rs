use ratatui::{Frame, crossterm::event::KeyEvent, layout::Rect};

pub(crate) mod counter;

pub(crate) trait Component {
    fn on_key_pressed(&mut self, key: KeyEvent);
    fn render(&mut self, frame: &mut Frame, area: Rect);
}
