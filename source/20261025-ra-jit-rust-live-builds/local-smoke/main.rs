fn answer() -> u32 { 42 }
fn main() { println!("{}", answer()); }
#[cfg(test)] mod tests { #[test] fn answer_matches() { assert_eq!(super::answer(), 42); } }
