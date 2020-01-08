/// Replacement for checked_pow() which is not yet in stable Rust.
/// Code "borrowed" from the standard library implementation.

pub trait CheckedPow: Sized {
    fn checked_pow(self, exp: u32) -> Option<Self>;
}

impl CheckedPow for i64 {
    fn checked_pow(self, mut exp: u32) -> Option<Self> {
        let mut base = self;
        let mut acc: Self = 1;

        while exp > 1 {
            if (exp & 1) == 1 {
                acc = acc.checked_mul(base)?;
            }
            exp /= 2;
            base = base.checked_mul(base)?;
        }

        // Deal with the final bit of the exponent separately, since
        // squaring the base afterwards is not necessary and may cause a
        // needless overflow.
        if exp == 1 {
            acc = acc.checked_mul(base)?;
        }

        Some(acc)
    }
}
