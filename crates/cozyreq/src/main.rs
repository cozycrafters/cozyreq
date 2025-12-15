fn main() -> color_eyre::Result<()> {
    color_eyre::install()?;
    cozyreq_tui::run()?;
    Ok(())
}
