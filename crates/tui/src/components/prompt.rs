use ratatui::{
    buffer::Buffer,
    crossterm::event::KeyEvent,
    layout::Rect,
    style::Style,
    widgets::{Block, Borders, Widget, WidgetRef},
};
use tui_textarea::TextArea;

use crate::components::Component;

pub(crate) struct Prompt {
    textarea: TextArea<'static>,
}

impl Default for Prompt {
    fn default() -> Self {
        let mut textarea = TextArea::default();
        textarea.set_block(Block::default().borders(Borders::ALL));
        textarea.set_placeholder_text("Describe the API requests you want to perform");
        textarea.set_cursor_line_style(Style::default());
        Self { textarea }
    }
}

impl Component for Prompt {
    fn on_key_pressed(&mut self, key: KeyEvent) {
        self.textarea.input(key);
    }
}

impl WidgetRef for Prompt {
    fn render_ref(&self, area: Rect, buf: &mut Buffer) {
        Widget::render(&self.textarea, area, buf);
    }
}
