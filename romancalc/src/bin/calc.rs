use romancalc as rc;

fn main() {
    let mut input = String::new();

    loop {
        use std::io::Write;
        input.clear();

        // Prompt user for input
        print!("Enter a calculation or q to quit: ");
        std::io::stdout().flush().expect("Could not flush");

        // Read input, trim whitespace
        if let Ok(_) = std::io::stdin().read_line(&mut input) {
            let trimmed = input.trim();

            if trimmed == "q" { break; }

            // For now just print parsed value
            match rc::Expression::parse_roman(trimmed) {
                Ok(expr) => match expr.evaluate() {
                    Some(value) => println!(
                        "{} = {} (= {})",
                        trimmed,
                        rc::numeral(value as u64)
                            .unwrap_or_else(|| "<Numeral Overflow>".into()),
                        value
                    ),
                    None => eprintln!("Overflow error.")
                },
                Err(e) => eprintln!("{}", e)
            }
        } else {
            break;
        }
    }
}
