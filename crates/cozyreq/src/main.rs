use color_eyre::Result;

fn main() -> Result<()> {
    color_eyre::install()?;
    cozyreq::cli::run()
}
