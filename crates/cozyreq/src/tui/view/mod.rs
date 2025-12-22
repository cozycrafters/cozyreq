use ratatui::{Frame, widgets::Paragraph};

use crate::tui::model::Model;

pub(crate) fn view(model: &mut Model, frame: &mut Frame) {
    frame.render_widget(
        Paragraph::new(format!("Counter: {}", model.counter)),
        frame.area(),
    );
}
