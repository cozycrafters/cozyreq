use color_eyre::Result;

fn main() -> Result<()> {
    color_eyre::install()?;
    cozyreq::tui::run()?;
    Ok(())
}
