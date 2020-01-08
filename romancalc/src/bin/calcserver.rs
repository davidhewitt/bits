/// Simple webserver to serve the roman numeral as a POST request

use actix_web::{
    server, App, AsyncResponder, Error, HttpMessage, HttpRequest, HttpResponse
};
use futures::{Future, Stream};
use serde_derive::Serialize;

use romancalc as rc;

#[derive(Serialize)]
struct CalculationResult {
    numeral: String,
    value: i64
}

#[derive(Serialize)]
struct CalculationError {
    error: String
}

fn calculate(req: &HttpRequest)
-> Box<Future<Item = HttpResponse, Error = Error>> {
    // Use actix's asynchronous API to concatenate the whole
    // body into one chunk to then operate on
    req.payload()
       .concat2()
       .from_err()
       .and_then(|body| {
            let expr = std::str::from_utf8(&body).unwrap();

            // Proccess the result and generate a calculation result
            // with both integer and numeral values (if possible)
            let result = rc::Expression::parse_roman(expr)
                .and_then(|expr| {
                    expr.evaluate().ok_or_else(|| "Integer Overflow".to_string())
                })
                .map(|value| CalculationResult {
                    numeral: rc::numeral_signed(value).unwrap_or_else(
                        || "<Roman Numeral Overflow>".to_string()
                    ),
                    value: value
                });

            // Finish up by either returning JSON calculation result, or
            // status 400 error with error text.
            Ok(match result {
                Ok(result) => HttpResponse::Ok()
                    .content_type("application/json")
                    .body(serde_json::to_string(&result).unwrap()),
                Err(error) => HttpResponse::BadRequest()
                    .body(serde_json::to_string(&CalculationError {error})
                                               .unwrap())
            })
       })
       .responder()
}

fn main() {
    let server = server::new(|| {
        App::new().resource("/", |r| r.method(http::Method::POST).f(calculate))
    });

    match server.bind("127.0.0.1:8000") {
        Ok(server) => {
            println!("Listening on port 8000");
            server.run()
        },
        Err(_) => eprintln!("Failed to bind to port 8000")
    }
}
