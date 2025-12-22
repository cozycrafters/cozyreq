#[tokio::main]
pub async fn main() -> color_eyre::Result<()> {
    color_eyre::install()?;
    let mut app = cozyreq_tui::App::new();
    app.run().await
}
