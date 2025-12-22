use cozyreq::tui;

#[tokio::main]
pub async fn main() -> color_eyre::Result<()> {
    color_eyre::install()?;
    tui::run().await
}
