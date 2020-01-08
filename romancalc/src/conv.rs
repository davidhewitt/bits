/// Functions to do with converting back and forth from roman numerals

/// Convert a single roman numeral character to a number
pub fn character_value(c: char) -> Result<u64, String> {
    match c {
        'I' => Ok(1),
        'V' => Ok(5),
        'X' => Ok(10),
        'L' => Ok(50),
        'C' => Ok(100),
        'D' => Ok(500),
        'M' => Ok(1000),
        _ => Err(format!("Unexpected character '{}'", c))
    }
}

/// Helper function to define the pairs such as IV that are allowed.
pub fn is_subtractive_pair(a: char, b: char) -> bool {
    match (a, b) {
        ('I', 'V') |
        ('I', 'X') |
        ('X', 'L') |
        ('X', 'C') |
        ('C', 'D') |
        ('C', 'M') => true,
        _ => false
    }
}

/// Convert an entire roman numeral string to a number
///
/// Returns a descriptive error in case of a failure. It may be
/// a nice extension to return also the position of the error
/// if that's the case.
pub fn numeral_value(numeral: &str) -> Result<u64, String> {

    if numeral.len() == 0 { return Err("Empty numeral".into()); }

    // We'll iterate over the chars of the string, and it'll be
    // handy to be able to peek at the char ahead.
    let mut chars = numeral.chars().peekable();

    // ASSUMPTION: It's not possible for roman numeral to overflow
    // a 64-bit unsigned number.
    let mut value = 0u64;
    let mut last_character_value = None;

    // Read all the values from the numeral one at a time
    while let Some(c) = chars.next() {
        let value_of_c = character_value(c)?;

        // If this is not the very first character, we need to
        // assert strictly decreasing
        if let Some(last) = last_character_value {
            if value_of_c >= last {
                return Err(format!("Character '{}' is not decreasing", c));
            }
        }

        // Record the last character value for future descending checks
        last_character_value = Some(value_of_c);

        // We now need to handle repetition and subtractive pairs
        // by peeking ahead to the next character(s)
        let mut repetition = 1;

        while let Some(&next) = chars.peek() {
            // Repetition
            if next == c {
                // Consume this value
                repetition += 1;
                chars.next();

                // May only repeat up to three times;
                if repetition > 3 {
                    return Err(
                        format!("Repetition of '{}' more than three times", c)
                    );
                }

                // Look for further repetition
                continue;
            }

            // Subtractive pair
            if repetition == 1 && is_subtractive_pair(c, next) {
                // Consume the next value and then add the value of the pair
                chars.next();
                value += character_value(next)? - value_of_c;

                // Set repetition to 0 so the value of c isn't added
                // back on later.
                repetition = 0;
            }
            break;
        }

        value += value_of_c * repetition;
    }

    Ok(value)
}

/// Roman numeral for a given integer
///
/// Returns None if x >= 4000
/// (outside range of numerals we wish to represent)
pub fn numeral(x: u64) -> Option<String> {
    let mut output = Vec::new();
    let mut remaining = x;

    // Cannot represent zero as roman numeral
    // Could use "nulla" ?
    if x == 0 {
        return None
    }

    while remaining > 0 {
        remaining -= match remaining {
            1000...3999 => {
                output.push('M');
                1000
            },
            900...999 => {
                output.push('C');
                output.push('M');
                900
            },
            500...899 => {
                output.push('D');
                500
            },
            400...499 => {
                output.push('C');
                output.push('D');
                400
            },
            100...399 => {
                output.push('C');
                100
            },
            90...99 => {
                output.push('X');
                output.push('C');
                90
            },
            50...89 => {
                output.push('L');
                50
            },
            40...49 => {
                output.push('X');
                output.push('L');
                40
            },
            10...39 => {
                output.push('X');
                10
            },
            9 => {
                output.push('I');
                output.push('X');
                9
            },
            5...8 => {
                output.push('V');
                5
            },
            4 => {
                output.push('I');
                output.push('V');
                4
            },
            1...3 => {
                output.push('I');
                1
            },
            _ => {
                // number is >= 4000
                return None;
            }
        }
    }

    assert!(remaining == 0);

    Some(output.into_iter().collect())
}

pub fn numeral_signed(x: i64) -> Option<String> {
    if x < 0 {
        Some(format!("-{}", numeral((-x) as u64)?))
    } else if x > 0 {
        numeral(x as u64)
    } else {
        // Note that zero is
        None
    }
}

#[cfg(test)]
mod test {

    use super::*;

    /// Check a few examples of numbers converting
    #[test]
    fn test_character_values() {
        // Check all known character values
        // NB can't (yet) iterate range of characters
        // so need to iterate a byte range and then cast
        // back to char inside the loop.
        for character in b'A'..=b'Z' {
            let character = character as char;
            let expected = match character {
                'I' => Some(1),
                'V' => Some(5),
                'X' => Some(10),
                'L' => Some(50),
                'C' => Some(100),
                'D' => Some(500),
                'M' => Some(1000),
                _ => None
            };

            assert_eq!(character_value(character).ok(), expected);
        }
    }

    #[test]
    fn test_sample_numerals() {
        let samples = vec![
            ("I", 1),
            ("II", 2),
            ("III", 3),
            ("IV", 4),
            ("V", 5),
            ("VI", 6),
            ("VII", 7),
            ("VIII", 8),
            ("IX", 9),
            ("X", 10),
            ("XXI", 21),
            ("XXVI", 26),
            ("XC", 90),
            ("MCML", 1950),

            // The only valid subtractions
            ("IV", 4),
            ("IX", 9),
            ("XL", 40),
            ("XC", 90),
            ("CD", 400),
            ("CM", 900)
        ];

        for (literal, expected) in samples {
            // Numeral -> integer
            assert_eq!(numeral_value(literal).unwrap(), expected);

            // Integer -> Numeral
            assert_eq!(literal, numeral(expected).unwrap());
        }
    }

    #[test]
    fn test_invalid_numerals() {
        let samples = vec![
            ("", "Empty numeral"),
            ("R", "Unexpected character 'R'"),
            ("IIII", "Repetition of 'I' more than three times"),
            ("VVVV", "Repetition of 'V' more than three times"),
            ("IVI", "Character 'I' is not decreasing"),
            ("MMCMCM", "Character 'C' is not decreasing"),
        ];

        for (literal, expected) in samples {
            assert_eq!(numeral_value(literal).err().unwrap(), expected);
        }
    }

    #[test]
    fn test_roundrips() {
        // Check that integer -> numeral -> integer
        // produces the original integer
        for i in 1..4000 {
            assert_eq!(numeral_value(&numeral(i).unwrap()).unwrap(), i);
        }
    }

    #[test]
    fn test_signed_numerals() {
        assert_eq!(numeral(0), None);
        assert_eq!(numeral_signed(0), None);

        for i in 0..4000 {
            assert_eq!(
                numeral_signed(-i),
                numeral(i as u64).map(|n| format!("-{}", n))
            )
        }
    }
}
