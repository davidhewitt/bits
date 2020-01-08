use romancalc as rc;

fn main() {
    let mut input = String::new();

    loop {
        use std::io::Write;
        input.clear();

        // Prompt user for input
        print!("Enter a roman numeral or q to quit: ");
        std::io::stdout().flush().expect("Could not flush");

        // Read input, trim whitespace
        if let Ok(_) = std::io::stdin().read_line(&mut input) {
            let numeral = input.trim();

            if numeral == "q" { break; }

            // For now just print parsed value
            match rc::numeral_value(numeral) {
                Ok(value) => println!("{} = {}", numeral, value),
                Err(e) => eprintln!("{}", e)
            }
        } else {
            break;
        }
    }
}
