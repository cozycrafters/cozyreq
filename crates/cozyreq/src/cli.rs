use clap::Parser;

#[derive(Parser)]
#[command(name = "cozyreq")]
#[command(about = "A cozy request tool", long_about = None)]
pub struct Cli {}

pub fn run() -> color_eyre::Result<()> {
    let _cli = Cli::parse();
    crate::tui::run()
}
