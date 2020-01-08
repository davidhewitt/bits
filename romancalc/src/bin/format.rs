use romancalc as rc;

fn main() {
    let mut input = String::new();

    loop {
        use std::io::Write;
        input.clear();

        // Prompt user for input
        print!("Enter a number or q to quit: ");
        std::io::stdout().flush().expect("Could not flush");

        // Read input, trim whitespace
        if let Ok(_) = std::io::stdin().read_line(&mut input) {
            let trimmed = input.trim();

            if trimmed == "q" { break; }

            // For now just print parsed value
            match trimmed.parse::<u64>() {
                Ok(value) => {
                    if value < 4000 {
                        println!("{} = {}", trimmed, rc::numeral(value).unwrap());
                    } else {
                        eprintln!("Can only handle values up to 4000");
                    }
                },
                Err(e) => eprintln!("{}", e)
            }
        } else {
            break;
        }
    }
}
