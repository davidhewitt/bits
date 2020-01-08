/// Representation of BODMAS operations
///
/// There's a lot of Box<Expression> because Expressions
/// cannot contain Expressions, just pointers to Expressions.
/// (Otherwise Expression would not have a well-defined size);
#[derive(Clone, Debug, PartialEq)]
pub enum Expression {
    /// Bracketed expression. Technically a no-op but here for faithfulness
    Brackets { expr: Box<Expression> },

    /// Raise to the power
    Order { base: Box<Expression>, exponent: Box<Expression> },

    /// Floor Division (as we're working with integers)
    Division { numerator: Box<Expression>, denominator: Box<Expression> },

    /// Multiplication
    Multiplication { lhs: Box<Expression>, rhs: Box<Expression> },

    /// Addition
    Addition { lhs: Box<Expression>, rhs: Box<Expression> },

    /// Subtraction
    Subtraction { lhs: Box<Expression>, rhs: Box<Expression> },

    /// Raw integer (positive or negative)
    Value(i64)
}

pub fn parse_integer(expr: &str) -> Result<i64, String> {
    expr.parse().map_err(|_| "Invalid number".into())
}

#[derive(Clone, Copy, Debug, PartialEq)]
enum Operator {
    Pow,
    Div,
    Mul,
    Add,
    Sub
}

impl std::fmt::Display for Operator {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>)
    -> Result<(), std::fmt::Error> {
        use Operator::*;
        formatter.write_str(match self {
            Pow => "^",
            Div => "/",
            Mul => "*",
            Add => "+",
            Sub => "-"
        })
    }
}


/// Helper struct to deal with the parsing of the expressions
struct ParserState {
    // Current in-progress pieces
    // These must all be empty when finish() is called
    // Sign of the next expression
    sign: Option<i64>,
    // Previously semi-complete expressions before one or more levels of brackets appeared
    outer_stacks: Vec<Vec<(Expression, Operator)>>,

    // The pieces of the overall expression.
    // When finish() is called they can be combined according to BODMAS
    // One or more previous terms, with the operator after them,
    // (eg. 1 + , 2 *)
    previous_terms: Vec<(Expression, Operator)>,
    // The last term parsed
    term: Option<Expression>
}

impl ParserState {
    fn new() -> Self {
        Self {
            sign: None,
            outer_stacks: vec![],
            previous_terms: vec![],
            term: None
        }
    }

    fn push_value(&mut self, v: i64) -> Result<(), String> {
        let expr = Expression::Value(v * self.sign.take().unwrap_or(1));
        match self.term {
            None => { self.term = Some(expr); Ok(()) }
            Some(_) => Err("Expected operator before value".into())
        }
    }

    fn push_operator(&mut self, op: Operator) -> Result<(), String> {
        match (self.term.take(), &self.sign, op) {
            (Some(expr), _, _) => {
                // There is a previous expression; push it and the operator
                // into the previous terms stack
                self.previous_terms.push((expr, op));
                Ok(())
            },
            (None, None, Operator::Add) => {
                // No preceding expression or sign; this is a plus sign
                self.sign = Some(1);
                Ok(())
            },
            (None, None, Operator::Sub) => {
                // No preceding expression or sign; this is a minus sign
                self.sign = Some(-1);
                Ok(())
            },
            _ => {
                // Anything else is an invalid time for an operator
                Err(format!("Unexpected operator '{}'", op))
            }
        }
    }

    fn open_bracket(&mut self) -> Result<(), String> {
        // For now don't support this
        if self.sign.is_some() {
            return Err("Cannot have bracket after sign".into())
        }

        // Opening bracket immediately after a term means multiplication
        if self.term.is_some() {
            self.push_operator(Operator::Mul)?;
        }

        // We're going a level deeper, so record the current level
        // and start a fresh one
        let mut current_stack = vec![];
        std::mem::swap(&mut current_stack, &mut self.previous_terms);
        self.outer_stacks.push(current_stack);

        assert!(self.previous_terms.is_empty());
        assert!(self.term.is_none());

        Ok(())
    }

    fn close_bracket(&mut self) -> Result<(), String> {
        if self.term.is_none() || self.sign.is_some() {
            return Err("Unexpected closing bracket".into());
        }

        // Restore the last stack
        let mut last_stack = match self.outer_stacks.pop() {
            Some(stack) => stack,
            None =>
                return Err("Closing bracket without opening bracket".into())
        };

        std::mem::swap(&mut self.previous_terms, &mut last_stack);

        self.term = Some(Expression::Brackets {
            expr: Box::new(ParserState::reduce_stack(
                last_stack,
                self.term.take().unwrap()
            ))
        });

        Ok(())
    }

    fn finish(mut self) -> Result<Expression, String> {
        if self.sign.is_some() {
            return Err("Expected value for sign at end of input".into())
        }

        if !self.outer_stacks.is_empty() {
            return Err("Unmatched opening bracket".into())
        }

        let last = match self.term {
            Some(expr) => expr,

            // No current term - either we had no input or
            // no input on the RHS of the last term
            None => return Err(match self.previous_terms.pop() {
                Some((_, op)) => format!("Unfinished operator: {}", op),
                None => "Empty input".into()
            })
        };

        Ok(ParserState::reduce_stack(self.previous_terms, last))
    }

    /// Bodmas-approved reduction of a chain of operators
    fn reduce_stack(
        previous_terms: Vec<(Expression, Operator)>,
        last: Expression
    ) -> Expression {
        use Operator::*;

        // Starting from the end and working backwards...
        let terms = previous_terms.into_iter().rev();

        // First pass: combine Order expressions
        let mut term = last;
        let mut combined_terms = vec![];

        for (next_term, op) in terms {
            match op {
                Pow => {
                    term = Expression::Order {
                        base: Box::new(next_term),
                        exponent: Box::new(term)
                    };
                },
                _ => {
                    combined_terms.push((term, op));
                    term = next_term;
                }
            }
        }

        // Now must work from front to back for Multiplication / Division
        // This is important to go from front to back because floor division
        // does not commute with multiplication
        let terms = combined_terms.into_iter().rev();
        let mut combined_terms = vec![];

        for (next_term, op) in terms {
            match op {
                Div => {
                    term = Expression::Division {
                        numerator: Box::new(term),
                        denominator: Box::new(next_term)
                    };
                },
                Mul => {
                    term = Expression::Multiplication {
                        lhs: Box::new(term),
                        rhs: Box::new(next_term)
                    };
                },
                _ => {
                    combined_terms.push((term, op));
                    term = next_term;
                }
            }
        }

        // Final pass: Addition & subtraction. Can work from back
        // to front again.
        let terms = combined_terms.into_iter().rev();

        for (next_term, op) in terms {
            match op {
                Add => {
                    term = Expression::Addition {
                        lhs: Box::new(next_term),
                        rhs: Box::new(term)
                    };
                },
                Sub => {
                    term = Expression::Subtraction {
                        lhs: Box::new(next_term),
                        rhs: Box::new(term)
                    };
                },
                _ => unreachable!()
            }
        }

        // And we're left with one final term!
        term
    }
}

#[derive(Debug, PartialEq)]
/// Token intermediary during parsing
///
/// NB originally considered building a structure which would
/// also contain the original position in the token. This could
/// then be used to report errors in subsequent phases of the
/// parser. For simpler code & in the interest of time I'm going
/// to skip that from this exercise.
enum ExpressionToken {
    OpeningBracket,
    ClosingBracket,
    Operator(Operator),
    Value(i64)
}

/// Simple parser which specifies a subrange of characters to
/// accept and can parse a bunch of them into an integer
trait IntegerParser {
    fn is_valid_char(value: char) -> bool;
    fn parse(expr: &str) -> Result<i64, String>;
}

struct DecimalParser;
struct RomanParser;

impl IntegerParser for DecimalParser {
    fn is_valid_char(value: char) -> bool {
        value >= '0' && value <= '9'
    }

    fn parse(expr: &str) -> Result<i64, String> {
        parse_integer(expr)
    }
}

impl IntegerParser for RomanParser {
    fn is_valid_char(value: char) -> bool {
        match value {
            'I' | 'V' | 'X' | 'L' | 'C' | 'D' | 'M' => true,
            _ => false
        }
    }

    fn parse(expr: &str) -> Result<i64, String> {
        crate::conv::numeral_value(expr).map(|u| u as i64)
    }
}

/// Convert expression to tokens.
fn tokenise<P: IntegerParser>(expr: &str)
-> Result<Vec<ExpressionToken>, String> {

    use ExpressionToken::*;
    use crate::expression::Operator::*;

    let mut output = Vec::new();

    let mut start = 0;
    let mut end = 0;

    let mut bytes = expr.as_bytes().into_iter().peekable();

    while bytes.peek().is_some() {
        let token = match bytes.next() {
            Some(b'(') => { start += 1; OpeningBracket },
            Some(b')') => { start += 1; ClosingBracket },
            Some(b'^') => { start += 1; Operator(Pow) },
            Some(b'*') => { start += 1; Operator(Mul) },
            Some(b'/') => { start += 1; Operator(Div) },
            Some(b'+') => { start += 1; Operator(Add) },
            Some(b'-') => { start += 1; Operator(Sub) },
            Some(&c) if P::is_valid_char(c as char) => {
                loop {
                    end += 1;
                    match bytes.peek() {
                        Some(&&c) if P::is_valid_char(c as char) => bytes.next(),
                        _ => break
                    };
                }

                let value = P::parse(expr.get(start..end).unwrap())?;

                start = end;
                Value(value)
            }
            Some(b' ') => { start += 1; end = start; continue },
            Some(c) => return Err(format!("Unexpected character '{}'", *c as char)),
            None => break
        };

        output.push(token);
        end = start;
    }

    Ok(output)
}


impl Expression {
    /// Parse an expression from a string containing integers
    pub fn parse(expr: &str) -> Result<Self, String> {
        Expression::parse_impl::<DecimalParser>(expr)
    }

    /// Parse an expression from a string containing roman numerals
    pub fn parse_roman(expr: &str) -> Result<Self, String> {
        Expression::parse_impl::<RomanParser>(expr)
    }

    /// Evaluate an expression to get the result
    ///
    /// Returns None if overflow occurred
    pub fn evaluate(&self) -> Option<i64> {
        use Expression::*;
        match self {
            Value(v) => Some(*v),
            Addition {lhs, rhs} =>
                lhs.evaluate()?.checked_add(rhs.evaluate()?),
            Subtraction {lhs, rhs} =>
                lhs.evaluate()?.checked_sub(rhs.evaluate()?),
            Multiplication {lhs, rhs} =>
                lhs.evaluate()?.checked_mul(rhs.evaluate()?),
            Division {numerator, denominator} =>
                numerator.evaluate()?.checked_div(denominator.evaluate()?),
            Order {base, exponent} => {
                use crate::checked_pow::CheckedPow;

                let exponent = exponent.evaluate()?;
                if exponent < 0 || exponent > u32::max_value() as i64 {
                    return None;
                }

                CheckedPow::checked_pow(base.evaluate()?, exponent as u32)
            },
            Brackets {expr} => expr.evaluate()
        }
    }

    /// Private implementation of parse methods
    fn parse_impl<P: IntegerParser>(expr: &str) -> Result<Self, String> {
        use ExpressionToken::*;

        // First convert the string to tokens, so that the code for
        // parsing is separate to the expression logic.
        let tokens = tokenise::<P>(expr)?;

        let mut parser_state = ParserState::new();

        for token in tokens {
            match token {
                OpeningBracket => parser_state.open_bracket()?,
                ClosingBracket => parser_state.close_bracket()?,
                Operator(op) => parser_state.push_operator(op)?,
                ExpressionToken::Value(v) => parser_state.push_value(v)?
            };
        }

        parser_state.finish()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use Expression::*;

    #[test]
    fn test_sample_expressions() {
        // Check basic parsing works as expected
        let samples = vec![
            ("1", Value(1)),
            ("-1", Value(-1)),
            ("1 + 1",
                Addition {lhs: Box::new(Value(1)), rhs: Box::new(Value(1))}),
            ("1 - 1",
                Subtraction {
                    lhs: Box::new(Value(1)),
                    rhs: Box::new(Value(1))
                }),
            ("1 + -1",
                Addition {lhs: Box::new(Value(1)), rhs: Box::new(Value(-1))}),
            ("1 * 1",
                Multiplication {
                    lhs: Box::new(Value(1)),
                    rhs: Box::new(Value(1))
                }),
            ("1 / 1",
                Division {
                    numerator: Box::new(Value(1)),
                    denominator: Box::new(Value(1))
                }),
            ("1 ^ 1", Order {
                    base: Box::new(Value(1)),
                    exponent: Box::new(Value(1))
                }),
            ("(1)", Brackets {expr: Box::new(Value(1))})
        ];

        for (expr, expected) in samples {
            dbg!(expr);
            assert_eq!(Expression::parse(expr).unwrap(), expected);
        }
    }

    #[test]
    fn test_sample_evaluations() {
        // Check some full evaluations yield correct numbers
        let samples = vec![
            ("1 + 1", 2),
            ("1 * 5", 5),
            ("1 + 1 * 2", 3),
            ("(1 + 1) * 2", 4),
            ("1 + 2 / 2", 2),
            ("(1 + 2) / 2", 1), // Because 3 / 2 floors to 1
            ("1 + 2 ^ 2", 5),
            ("(1 + 2) ^ 2", 9),
            ("-1 * 10", -10),
            ("-100", -100),
            ("10 ^ 2 * 13", 1300),
            ("10 ^ 2 * -13", -1300),
            ("10 ^ (2 * 2)", 10000),
            ("10 / -3", -3),
            ("10 / -3 + 4", 1),
            ("(-100 * 2) + (6 - 10) ^ 2", -184),
        ];

        for (expr, expected) in samples {
            dbg!(expr);
            assert_eq!(
                Expression::parse(expr).unwrap().evaluate().unwrap(),
                expected
            );
        }
    }

    #[test]
    fn test_parse_integer() {
        // Confirm integer parsing works as expected
        assert_eq!(parse_integer("100").unwrap(), 100);
        assert_eq!(parse_integer("+100").unwrap(), 100);
        assert_eq!(parse_integer("-64").unwrap(), -64);
    }

    #[test]
    fn test_tokenise() {
        use ExpressionToken::*;
        use super::Operator::*;
        let samples = vec![
            ("1", vec![Value(1)]),
            ("-1", vec![Operator(Sub), Value(1)]),
            ("1 + 1", vec![Value(1), Operator(Add), Value(1)]),
            ("1 - 1", vec![Value(1), Operator(Sub), Value(1)]),
            ("1 + -1", vec![Value(1), Operator(Add), Operator(Sub), Value(1)]),
            ("1 / 1", vec![Value(1), Operator(Div), Value(1)]),
            ("1 ^ 1", vec![Value(1), Operator(Pow), Value(1)]),
            ("(1)", vec![OpeningBracket, Value(1), ClosingBracket])
        ];

        for (expr, expected) in samples {
            dbg!(expr);
            assert_eq!(tokenise::<DecimalParser>(expr).unwrap(), expected);
        }
    }

    #[test]
    fn test_tokenise_roman() {
        use ExpressionToken::*;
        use super::Operator::*;
        let samples = vec![
            ("I", vec![Value(1)]),
            ("-IV", vec![Operator(Sub), Value(4)]),
            ("VI + L", vec![Value(6), Operator(Add), Value(50)]),
            ("MMC - IX", vec![Value(2100), Operator(Sub), Value(9)]),
            ("XI + -D", vec![Value(11), Operator(Add), Operator(Sub), Value(500)]),
            ("CD / XC", vec![Value(400), Operator(Div), Value(90)]),
            ("M ^ II", vec![Value(1000), Operator(Pow), Value(2)]),
            ("(CLI)", vec![OpeningBracket, Value(151), ClosingBracket])
        ];

        for (expr, expected) in samples {
            dbg!(expr);
            assert_eq!(tokenise::<RomanParser>(expr).unwrap(), expected);
        }
    }
}
