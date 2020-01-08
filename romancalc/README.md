RomanCalc
=========

A roman numeral calculator written in Rust. (Using Rust 1.32.0)

I chose to use the Rust programming language because I find it enjoyable and reliable to work with. Additionally its pattern matching is very expressive and felt suitable for writing a program for numerical expressions.

In case you're unfamiliar with Rust, you can install rustup (the recommended way to install and update Rust) from <https://rustup.rs/>

Once the Rust tools are on your PATH, execute:

- `cargo run --bin calc` to launch the roman numeral calculator
- `cargo run --bin parse` to launch the roman numeral parse program
- `cargo run --bin format` to launch the roman numeral format program
- `cargo test` to run the tests
- `cargo doc --no-deps --open` to view the documentation

## Webserver

Use `cargo run --bin calcserver` to launch a webserver on localhost:8000.

To access it submit a POST request to / , with the calculation to process as the body text. The server will then return a JSON object like:

    {
        "numeral": "Some roman numeral" or "<Roman Numeral Overflow>"
        "value": <some integer>,
    }

The `<Roman Numeral Overflow>` will be received when the calculation result is outside of the bounds of a Roman numeral.

If the POST request is invalid (e.g. badly written calculation) then the server will return status 400 with a JSON body containing an `error` field.
