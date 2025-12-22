use cozyreq_tui::App;
use insta::assert_snapshot;
use ratatui::{
    Terminal,
    backend::TestBackend,
    crossterm::event::{KeyCode, KeyEvent},
};

#[test]
fn test_render_app() {
    let app = App::new();
    let mut terminal = Terminal::new(TestBackend::new(80, 20)).unwrap();
    terminal
        .draw(|frame| frame.render_widget(&app, frame.area()))
        .unwrap();
    assert_snapshot!(terminal.backend());
}

#[test]
fn test_render_app_after_j_pressed_three_times() {
    let mut app = App::new();
    for _ in 0..3 {
        app.on_key_pressed(KeyEvent::from(KeyCode::Char('j')));
    }
    let mut terminal = Terminal::new(TestBackend::new(80, 20)).unwrap();
    terminal
        .draw(|frame| frame.render_widget(&app, frame.area()))
        .unwrap();
    assert_snapshot!(terminal.backend());
}
