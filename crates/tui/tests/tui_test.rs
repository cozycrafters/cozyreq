use cozyreq_tui::App;
use insta::assert_snapshot;
use ratatui::{Terminal, backend::TestBackend};

#[test]
fn test_render_app() {
    let app = App::new();
    let mut terminal = Terminal::new(TestBackend::new(80, 20)).unwrap();
    terminal
        .draw(|frame| frame.render_widget(&app, frame.area()))
        .unwrap();
    assert_snapshot!(terminal.backend());
}
